import nibabel as nb
import numpy as np
from skimage.exposure import match_histograms


def get_sub_list(file):
    with open(file) as f:
        sub_list = f.readlines()
    f.close()
    return sub_list


def get_nii_info(img_path):
    img = nb.load(img_path)
    affine = img.affine
    img_fdata = img.get_fdata()
    header = img.header
    return affine, img_fdata, header


def save_img(affine, img_fdata, header, path):
    cropped_img = nb.Nifti1Image(img_fdata, affine, header)
    nb.save(cropped_img, path)


def get_first_and_last_zero(array_sample):
    for i in range(len(array_sample)):
        if array_sample[i - 1] != 0:
            first_non_zero = i
            break

    i = len(array_sample) - 1
    while i >= 0:
        if array_sample[i] != 0:
            last_non_zero = i
            break
        i -= 1
    return first_non_zero, last_non_zero


def crop_img(img_path, img_cropped_path):
    affine, img_fdata, header = get_nii_info(img_path)
    middle_point = np.floor(np.shape(img_fdata)[2] / 2).astype(np.int)

    _, _, z_dims = header.get_zooms()
    img_center_slices = np.floor(120 / z_dims).astype(np.int)
    img_nozero_slices = np.floor(img_center_slices / 2).astype(np.int)

    min = middle_point - img_nozero_slices
    max = middle_point + img_nozero_slices
    img_cropped = img_fdata[:, :, :]
    img_cropped[:, :, :min] = 0
    img_cropped[:, :, max:] = 0
    save_img(affine, img_cropped, header, img_cropped_path)


def collage_img(img_cropped_path, img_add_path, img_frankestein_path):
    affine, img_cropped_fdata, header = get_nii_info(img_cropped_path)
    _, img_add_fdata, _ = get_nii_info(img_add_path)

    # Rescale Intensity
    for j in np.arange(np.shape(img_cropped_fdata)[1]):
        img_add_fdata[:, j, :] = match_histograms(img_add_fdata[:, j, :], img_cropped_fdata[:, j, :])
    img_frankestein = img_cropped_fdata
    first_non_zero, last_non_zero = get_first_and_last_zero(img_frankestein[128, 128, :])
    img_frankestein[:, :, :first_non_zero - 1] = img_add_fdata[:, :, :first_non_zero - 1]
    img_frankestein[:, :, last_non_zero + 1:] = img_add_fdata[:, :, last_non_zero + 1:]
    img_frankestein_path = img_frankestein_path
    save_img(affine, img_frankestein, header, img_frankestein_path)


def zero_pad(img_pad_path, img_reference, img_zeropadded_path):
    affine_pad, img_pad_fdata, header_pad = get_nii_info(img_pad_path)
    _, img_ref_fdata, header_ref = get_nii_info(img_reference)

    img_ref_shape = np.shape(img_ref_fdata)
    img_ref_dims = header_ref.get_zooms()
    z_ref_fov = img_ref_shape[0] * img_ref_dims[0]
    print(z_ref_fov, img_ref_dims, img_ref_shape)

    img_pad_shape = np.shape(img_pad_fdata)
    img_pad_dims = header_pad.get_zooms()
    z_pad_fov = img_pad_shape[0] * img_pad_dims[0]
    print(z_pad_fov, img_pad_shape, img_pad_dims)

    diff_in_mm = z_ref_fov - z_pad_fov
    zeros_add = np.round(diff_in_mm / img_pad_dims[0])
    zeros_add = np.floor(zeros_add / 2.) * 2
    padded_shape = np.array([img_pad_shape[0] + zeros_add, img_pad_shape[1], img_pad_shape[2]]).astype(np.int)
    img_padded_fdata = np.zeros(padded_shape)
    min = np.int(zeros_add / 2)
    max = np.int(padded_shape[0] - min)
    img_padded_fdata[min:max, :, :] = img_pad_fdata

    print(affine_pad)
    affine_pad[:, 3] = [affine_pad[0, 3] - zeros_add / 2, affine_pad[1, 3] - 1, affine_pad[2, 3] + 2, affine_pad[3, 3]]
    print(affine_pad)
    img_padded = nb.Nifti1Image(img_padded_fdata, affine_pad)
    nb.save(img_padded, img_zeropadded_path)


def trim(img_cropped_path, img_ds_path, trim_image_path):
    img_cropped_affine, img_cropped_fdata, img_cropped_header = get_nii_info(img_cropped_path)
    img_ds_affine, img_ds_fdata, img_ds_header = get_nii_info(img_ds_path)

    img_cropped_shape = np.shape(img_cropped_fdata)
    img_ds_shape = np.shape(img_ds_fdata)

    abc_cropped = np.around(img_cropped_affine[:3, 3], 2)
    abc_ds = np.around(img_ds_affine[:3, 3], 2)  # Translation vector of the image, for the case of the [0, 0, 0]
    # voxels it tells how far it is from the center of the image in spatial coordinates (0, 0, 0)

    img_dims = img_ds_header.get_zooms()  # Dimension of the voxels in each direction,
    # it assumes that both  images have the same dimensions

    # For all the axis we assume that if the dimensions of both matrices are not the exact same,
    # and the [0, 0, 0] voxels of both images are at a similar distance from the spatial center, then the error in
    # matrix shape is due to extra voxels in the far ends of the matrices.

    diff_abc = abs(abc_cropped) - abs(abc_ds)
    new_shape = img_ds_shape
    print(new_shape, img_cropped_shape)
    num_slices_trimx, num_slices_addx, num_slices_trimmax_x, num_slices_add2x, new_shape = get_trims(img_ds_shape[0],
                                                                                                     img_cropped_shape[
                                                                                                         0],
                                                                                                     diff_abc[0],
                                                                                                     img_dims[0],
                                                                                                     new_shape,
                                                                                                     0)

    num_slices_trimy, num_slices_addy, num_slices_trimmax_y, num_slices_add2y, new_shape = get_trims(img_ds_shape[1],
                                                                                                     img_cropped_shape[
                                                                                                         1],
                                                                                                     diff_abc[1],
                                                                                                     img_dims[1],
                                                                                                     new_shape,
                                                                                                     1)

    num_slices_trimz, num_slices_addz, num_slices_trimmax_z, num_slices_add2z, new_shape = get_trims(img_ds_shape[2],
                                                                                                     img_cropped_shape[
                                                                                                         2],
                                                                                                     diff_abc[2],
                                                                                                     img_dims[2],
                                                                                                     new_shape,
                                                                                                     2)
    print(new_shape)
    new_image = np.zeros(new_shape)
    new_image[num_slices_addx:new_shape[0] - num_slices_add2x, num_slices_addy:new_shape[1] - num_slices_add2y,
              num_slices_addz:new_shape[2] - num_slices_add2z] = img_ds_fdata[
                                                               num_slices_trimx:img_ds_shape[0] - num_slices_trimmax_x,
                                                               num_slices_trimy:img_ds_shape[1] - num_slices_trimmax_y,
                                                               num_slices_trimz:img_ds_shape[2] - num_slices_trimmax_z]

    save_img(img_cropped_affine, new_image, img_cropped_header, trim_image_path)


def get_trims(img_ds_shape, img_cropped_shape, diff_abc, img_dims, new_shape, ind):
    num_slices_trim = 0
    num_slices_add = 0
    num_slices_trimmax = 0
    num_slices_add2 = 0
    new_image = np.zeros(new_shape)
    if img_ds_shape != img_cropped_shape:
        if abs(diff_abc) > img_dims / 2 and diff_abc < 0:
            num_slices_add = np.round(abs(diff_abc / img_dims)).astype(int)
            print("Slice to add at the beginning: ", num_slices_add)
            add_ar = np.array([0, 0, 0])
            add_ar[ind] = num_slices_add
            new_image = np.zeros(new_shape + add_ar)
        elif abs(diff_abc) > img_dims / 2 and diff_abc > 0:
            num_slices_trim = np.round(abs(diff_abc / img_dims)).astype(int)
            add_ar = np.array([0, 0, 0])
            add_ar[ind] = num_slices_trim
            new_image = np.zeros(new_shape - add_ar)
            print("Slices to delete from the beginning: ", num_slices_trim)
        else:
            new_image = np.zeros(new_shape)

        new_shape = np.shape(new_image)
        print(new_shape)
        if new_shape[ind] != img_cropped_shape:
            if new_shape[ind] > img_cropped_shape:
                num_slices_trimmax = new_shape[ind] - img_cropped_shape
                add_ar = np.array([0, 0, 0])
                add_ar[ind] = num_slices_trimmax
                new_image = np.zeros(new_shape - add_ar)
                print("Slices to delete from the end: ", num_slices_trimmax)
            else:
                num_slices_add2 = img_cropped_shape - new_shape[ind]
                add_ar = np.array([0, 0, 0])
                add_ar[ind] = num_slices_add2
                new_image = np.zeros(new_shape + add_ar)
                print("Slices to add at the end: ", num_slices_add2)

    new_shape = np.shape(new_image)

    return num_slices_trim, num_slices_add, num_slices_trimmax, num_slices_add2, new_shape
