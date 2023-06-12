# This is a sample Python script.
from chart_studio import plotly
import plotly.utils
# Press âŒƒR to execute it or replace it with your code.
# Press Double â‡§ to search everywhere for classes, files, tool windows, actions, and settings.

from flask import Flask, render_template, request, Response

import json
import pydicom as dicom
import numpy as np
import os
import glob
import matplotlib
import matplotlib.pyplot as plt
import scipy.ndimage
from skimage.measure import label, regionprops, regionprops_table
from scipy.ndimage.morphology import binary_fill_holes, binary_closing, binary_dilation, binary_erosion, binary_opening
import pandas as pd
import skimage
from skimage import morphology
import time
import nrrd
from skimage import measure
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import chart_studio.plotly as py
from plotly.tools import FigureFactory as FF
import plotly.graph_objects as go
from plotly.graph_objs import *
# from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.signal import convolve2d

app = Flask(__name__)


stored_dicom_ct_path = None
stored_seriesuid = None
trajectory_df = None
resampled_arr = None
perm_arr_hu = None
perm_brain_skull_mask = None


#Inputs for the user-interface
@app.route("/submit_inputs", methods=["GET", "POST"])
def submit_inputs():

    DICOM_FOLDER_PATH = request.form['DICOM_FOLDER_PATH']
    SERIES_UID = request.form['SERIES_UID']
    SERIES_UID = None if SERIES_UID.lower() == 'none' else SERIES_UID
    SPACING = 1.0
    LARGEST_REGION_INDEX = int(request.form['LARGEST_REGION_INDEX'])
    ERODE_DILATE_ITER = int(request.form['ERODE_DILATE_ITER'])
    SEGPATH = None
    MID_PUPILLARY_Z_INDEX = int(request.form['MID_PUPILLARY_Z_INDEX'])
    RIGHT = request.form['RIGHT']
    RIGHT = True if RIGHT.lower() == 'true' else False
    OFFSET = 0
    SENS_VENT = int(request.form['SENS_VENT'])
    ROT_UP_DOWN = int(request.form['ROT_UP_DOWN'])
    ROT_LEFT_RIGHT = int(request.form['ROT_LEFT_RIGHT'])
    SHIFT_LEFT_RIGHT = int(request.form['SHIFT_LEFT_RIGHT'])


    print('getting to submit inputs function end')
    return return_3D_image(DICOM_FOLDER_PATH, SERIES_UID, SPACING, LARGEST_REGION_INDEX, ERODE_DILATE_ITER, SEGPATH,
                    MID_PUPILLARY_Z_INDEX, RIGHT, OFFSET, SENS_VENT, ROT_UP_DOWN, ROT_LEFT_RIGHT, SHIFT_LEFT_RIGHT)


@app.route('/')
def make_home():
    return render_template('index.html', graphJSON='', diceScore='')

def return_3D_image(DICOM_FOLDER_PATH, SERIES_UID, SPACING, LARGEST_REGION_INDEX, ERODE_DILATE_ITER, SEGPATH,
                    MID_PUPILLARY_Z_INDEX, RIGHT, OFFSET, SENS_VENT,
                    ROT_UP_DOWN, ROT_LEFT_RIGHT, SHIFT_LEFT_RIGHT):

    #Start timer to record time-elapsed
    print('Starting Timer')
    st_time = time.time()

    global resampled_arr
    global perm_arr_hu
    global perm_spacing
    global stored_dicom_ct_path
    global stored_seriesuid
    global perm_brain_skull_mask
    #Load in Dicom files
    if resampled_arr is None or stored_dicom_ct_path != DICOM_FOLDER_PATH or stored_seriesuid != SERIES_UID:
        slices = load_scan(DICOM_FOLDER_PATH)
        arr1 = []
        for aslice in slices:
            arr1.append(aslice.SeriesInstanceUID)

        uniq_series_uids = np.unique(arr1, return_counts=True)
        print(uniq_series_uids)

        if SERIES_UID:
            arr = []
            for aslice in slices:
                if aslice.SeriesInstanceUID == SERIES_UID:
                    arr.append(aslice)
        else:
            arr = slices
        #Convert to Hounsfield units (HU)
        arrhu = get_pixels_hu(arr)
        print("Slice Thickness: %f" % slices[0].SliceThickness)
        print("Pixel Spacing (row, col): (%f, %f) " % (slices[0].PixelSpacing[0], slices[0].PixelSpacing[1]))

        #Resample to standardize the spacing of the slices
        print ("Shape before resampling\t", arrhu.shape)
        arr2, spacing = resample(arrhu, arr, [SPACING, SPACING, SPACING])
        print ("Shape after resampling\t", arr2.shape)

        #Making skull mask by using HU of 200 as threshold for bone
        print('Making skull mask')
        brain_skull_mask = binary_dilation(arr2 > 200, iterations=3)
        brain_skull_mask = binary_closing(brain_skull_mask, structure=np.ones((5, 5, 5)))
        print('Labeling skull mask')
        label_skull = label(brain_skull_mask)
        regions_skull = regionprops_table(label_skull, properties=('bbox', 'area', 'label'))
        props_skullDF = pd.DataFrame(regions_skull)
        props_skullDF = props_skullDF.sort_values('area', ascending=False)
        props_skullDF = props_skullDF.sort_values('area', ascending=False)
        brain_skull_mask = (label_skull == props_skullDF.iloc[0].label).astype(int)
        resampled_arr = arr2.copy()
        perm_arr_hu = arrhu.copy()
        perm_spacing = spacing.copy()
        perm_brain_skull_mask = brain_skull_mask.copy()
        stored_dicom_ct_path = DICOM_FOLDER_PATH
        stored_seriesuid = SERIES_UID
    else:
        arr2 = resampled_arr.copy()
        arrhu = perm_arr_hu.copy()
        spacing = perm_spacing.copy()
        brain_skull_mask = perm_brain_skull_mask.copy()


    #print("before rotation", brain_skull_mask.max(), brain_skull_mask.min())

    #Option for rotating image up or down
    arr2 = scipy.ndimage.rotate(arr2, angle=ROT_UP_DOWN, axes=(1, 0), reshape=False, order=3, mode='constant', cval=arr2.min(), prefilter=True)
    brain_skull_mask = scipy.ndimage.rotate(brain_skull_mask, angle=ROT_UP_DOWN, axes=(1, 0), reshape=False, order=3, mode='constant',
                                cval=brain_skull_mask.min(), prefilter=True)

    #Option for rotating image left or right
    arr2 = scipy.ndimage.rotate(arr2, angle=ROT_LEFT_RIGHT, axes=(1, 2), reshape=False, order=3, mode='constant', cval=arr2.min(),
                                prefilter=True)
    brain_skull_mask = scipy.ndimage.rotate(brain_skull_mask, angle=ROT_LEFT_RIGHT, axes=(1, 2), reshape=False, order=3, mode='constant',
                                cval=brain_skull_mask.min(),
                                prefilter=True)

    #Adjust Z index of nasion based on changes made due to input values
    MID_PUPILLARY_Z_INDEX = int((arrhu.shape[0] - MID_PUPILLARY_Z_INDEX)*spacing[0]/SPACING)
    print('new pupillary z', MID_PUPILLARY_Z_INDEX)

    delta_y_pup = int(100/SPACING * np.sin(np.deg2rad(ROT_UP_DOWN))) #100 is the distance from center of brain to estimated location of original nasion.
    MID_PUPILLARY_Z_INDEX += delta_y_pup
    print('adjusted pupillary z', MID_PUPILLARY_Z_INDEX)

    #Set threshold
    arr3 = ((arr2 < SENS_VENT) * (arr2 > -10)).astype(int)

    #Erode to disconnect any non-ventricle regions from the ventricles
    print('Closing and Eroding')
    arr4 = binary_closing(arr3, structure=np.ones((3, 3, 3)))
    if ERODE_DILATE_ITER > 0:
        arr5 = binary_erosion(arr4, iterations=ERODE_DILATE_ITER)
    else:
        arr5 = arr4.copy()

    label_eroded = label(arr5)
    print('Calculating regionprops')
    regions_eroded = regionprops_table(label_eroded, properties=('bbox', 'area', 'label'))
    props_erodedDF = pd.DataFrame(regions_eroded)
    props_erodedDF = props_erodedDF.sort_values('area', ascending=False)

    #Dilate the segmented ventricle to undo the erosion we did above (beecause connections have already been severed from before)
    arr7 = ((label_eroded == props_erodedDF.iloc[LARGEST_REGION_INDEX].label)).astype(int)
    print('Dilating')
    if ERODE_DILATE_ITER > 0:
        arr7 = binary_dilation(arr7, structure=np.ones((3, 3, 3)), iterations=ERODE_DILATE_ITER)
    print()
    # Show final binary mask of ventricles (arr7)
    # Show final binary mask of ventricles (arr7)
    # sample_stack(arr7)

    v, f = make_mesh(arr7, 0.5, 1)
    store_faces_vertices(f, v)

    #Calculating the dice score
    dice_score = ''
    if SEGPATH:
        manual_mask, header = nrrd.read(SEGPATH)
        print("Shape before resampling\t", manual_mask.shape)
        arr_mask, spacing = resample_nrrd(manual_mask, header, [SPACING, SPACING, SPACING])
        print("Shape after resampling\t", arr_mask.shape)

        arr_mask2 = np.swapaxes(arr_mask, 0, 2)
        print('shape:', arr_mask2.shape)

        dice_score = dice(arr7, arr_mask2)
        print(dice_score)

    #Finding 3 edge points on either side of the skull
    edge_points = get_edgepoints(brain_skull_mask[MID_PUPILLARY_Z_INDEX, :, :])

    # Finding the sagittal midpoint
    tot_sl = brain_skull_mask.shape[0]
    sl_sampled = brain_skull_mask[[int(tot_sl * 0.2), int(tot_sl * 0.3), int(tot_sl * 0.4), int(tot_sl * 0.7), int(tot_sl * 0.8)], :, :]
    midpts = []
    for sl_ in sl_sampled:
        edg_pts = get_edgepoints(sl_)
        x_pts = np.array([i[1] for i in edg_pts])
        this_midpt = (np.min(x_pts) + np.max(x_pts)) / 2
        midpts.append(this_midpt)


    sag_midpt = int(np.median(midpts))

    print('SAG_MIDPT', sag_midpt, midpts)
    candidate_x_y_points = [x for x in edge_points if x[1] == sag_midpt]


    #Starting from the nasion, going up 11 cm
    print('Going up 11 cm')
    fin_distance = 110
    cur_dist = 0
    cur_index = MID_PUPILLARY_Z_INDEX
    prev_x = candidate_x_y_points[0][1]
    prev_y = candidate_x_y_points[0][0]
    starting_point = (cur_index, prev_y, prev_x)
    while cur_dist < fin_distance:
        cur_index += 1
        edge_points = get_edgepoints(brain_skull_mask[cur_index, :, :])

        all_valid_ep = [x for x in edge_points if x[1] == sag_midpt]
        dists = [np.sqrt((x[0] - prev_y) ** 2 + (x[1] - prev_x) ** 2 + (cur_index - cur_index - 1) ** 2) for x in
                 all_valid_ep]
        min_dist = np.min(dists)
        min_dist_pt = all_valid_ep[dists.index(min_dist)]

        cur_dist += min_dist * SPACING
        prev_x = min_dist_pt[1]
        prev_y = min_dist_pt[0]

        print(cur_index, cur_dist, min_dist) #, all_valid_ep, dists, min_dist_pt)

    final_point = (cur_index, prev_y, prev_x)

    #Going right or left 3 cm to the entrance point for EVD
    print('Going left/right 3 cm')
    fin_distance = 30
    cur_dist = 0
    cur_index = final_point[0]
    cur_point = list(final_point)

    while cur_dist < fin_distance:
        cur_index -= 1
        edge_points = get_edgepoints(brain_skull_mask[cur_index, :, :])
        if RIGHT:
            all_valid_ep = [x for x in edge_points if x[0] == final_point[1] and x[1] <= final_point[2]]
        else:
            all_valid_ep = [x for x in edge_points if x[0] == final_point[1] and x[1] >= final_point[2]]
        dists = [np.sqrt((x[0] - prev_y) ** 2 + (x[1] - prev_x) ** 2 + (cur_index - cur_index - 1) ** 2) for x in
                 all_valid_ep]
        min_dist = np.min(dists)
        min_dist_pt = all_valid_ep[dists.index(min_dist)]

        cur_dist += min_dist * SPACING
        prev_x = min_dist_pt[1]
        prev_y = min_dist_pt[0]

        print(cur_index, cur_dist, min_dist)

    kocher_point = (cur_index, prev_y, prev_x)

    ventricle_sideview = arr7.max(axis=2)
    vent_edgepts = get_edgepoints(ventricle_sideview)
    x = [i[1] for i in vent_edgepts]
    y = [i[0] for i in vent_edgepts]
    ventricle_sideview_cropped = ventricle_sideview[np.min(y):np.max(y), np.min(x):np.max(x)]

    x_min = np.min(x)
    y_min = np.min(y)

    front_ventricle = ventricle_sideview_cropped[:, :ventricle_sideview_cropped.shape[1] // 2]
    vent_edgpts2 = get_edgepoints(front_ventricle)

    x_pts = [i[1] for i in vent_edgpts2]
    y_pts = [i[0] for i in vent_edgpts2]

    while x_pts[np.argmax(y_pts)] > np.max(x_pts) - 10:
        print('in')
        front_ventricle = front_ventricle[:, 0:-2]
        vent_edgpts2 = get_edgepoints(front_ventricle)
        x_pts = [i[0] for i in vent_edgpts2]
        y_pts = [i[1] for i in vent_edgpts2]

    bottom_ventricle_y = np.min(y_pts)
    bottom_ventricle_x = x_pts[np.argmin(y_pts)]

    targetidx = None

    if RIGHT:
        targetidx = props_erodedDF.iloc[[0, 1]]["bbox-2"].idxmin()
    else:
        targetidx = props_erodedDF.iloc[[0, 1]]["bbox-2"].idxmax()
    arr_rv = (label_eroded == props_erodedDF.loc[targetidx].label).astype(int)

    arr_rv = binary_dilation(arr_rv, structure=np.ones((3, 3, 3)), iterations=2)

    arr_rv_slice = arr_rv[bottom_ventricle_y + y_min + OFFSET, :, :]

    edg_pts = get_edgepoints(arr_rv_slice)
    x_pts = np.array([i[1] for i in edg_pts])
    y_pts = np.array([i[0] for i in edg_pts])


    z_val = sag_midpt - SHIFT_LEFT_RIGHT



    if SERIES_UID:
        ventricle_pt = [bottom_ventricle_y + y_min + OFFSET, bottom_ventricle_x + x_min, z_val]
    else:
        ventricle_pt = [bottom_ventricle_y + y_min + OFFSET, bottom_ventricle_x + x_min, z_val]

    #Given kosher_pt, ventricle_pt, and ventricle mask, calculate the lowest possible offset.
    ventricle_pt = calc_offset_ventricle_pt(kocher_point, ventricle_pt, arr7)

    #Masking meshses
    print('Making meshes')
    v, f = make_mesh(brain_skull_mask, 0.5, 4)
    v_ven, f_ven = make_mesh(arr7, 0.5, 4) # arr7 is the final ventricle mask

    #Drawing skull
    print("Drawing skull")
    fig_skull = plotly_3d_v2(v, f)

    fig_skull.add_trace(go.Scatter3d(x=[kocher_point[2], starting_point[2]],
                                     y=[kocher_point[1], starting_point[1]],
                                     z=[kocher_point[0], starting_point[0]],
                                     mode='markers'))

    fig_skull.add_trace(go.Scatter3d(x=[kocher_point[2], ventricle_pt[2]],
                                     y=[kocher_point[1], ventricle_pt[1]],
                                     z=[kocher_point[0], ventricle_pt[0]], mode='lines',
                                     line=dict(width=6)))

    store_trajectory(kocher_point, ventricle_pt, SERIES_UID)

    #Drawing ventricle
    print("Drawing ventricle")
    fig_ventricle = plotly_3d_v2(v_ven, f_ven, cmap='rainbow')

    #Putting figure together
    print("Putting Figure together")
    fig = go.Figure(data=[fig_skull.data[0], fig_ventricle.data[0], fig_skull.data[2], fig_skull.data[3]])

    fig['data'][0].update(opacity=0.5)
    fig['data'][1].update(opacity=0.5)

    fig_ret = plot(fig, include_plotlyjs=False, output_type='div') # NOTE THIS WAS USED FOR THE ONLINE VERSION

    graphJSON = json.dumps(fig_ret, cls=plotly.utils.PlotlyJSONEncoder)
    fig_ret = fig_ret.replace("<div>", '<div style="height:100vh">')
    fig_ret = fig_ret.replace('script type="text/javascript"', 'script type="text/javascript" id="chart_script"')
    if dice_score:

        fig_ret = fig_ret.replace('</div>', '</div> <div> <h2 class="align_center"> Dice Score: %0.3f </h2> </div>' % dice_score, 1)

    print('Time Taken: %s seconds' % (time.time() - st_time))

    return fig_ret  # render_template('index.html', graphJSON=fig_ret, diceScore=dice_score)



#Function for loading in scans
def load_scan(path):
    slices = [dicom.read_file(s) for s in glob.glob(path + "/*.dcm")]

    try:
        slices.sort(key=lambda x: int(x.ImagePositionPatient[2]))
        print([x.ImagePositionPatient[2] for x in slices])

    except:
        slices.sort(key=lambda x: int(x.InstanceNumber))
        print([x.InstanceNumber for x in slices])


    try:
        # print('Image Position Patient', slices[0].ImagePositionPatient, slices[-1].ImagePositionPatient, slices[2].ImagePositionPatient)
        # slice_thickness = np.median([np.abs(slices[x].ImagePositionPatient[2] - slices[x-1].ImagePositionPatient[2]) for x in range(1, len(slices))])
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:

        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices

#Coverting pixels ot Hounsfield units (HU)
def get_pixels_hu(scans):
    image = np.stack([s.pixel_array for s in scans])
    image = image.astype(np.int16)

    #Set outside-of-scan pixels to 1
    image[image == -2000] = 0

    #Convert to Hounsfield units (HU)
    intercept = scans[0].RescaleIntercept
    slope = scans[0].RescaleSlope

    if slope != 1:
        image = slope * image.astype(np.float64)
        image = image.astype(np.int16)

    image += np.int16(intercept)

    return np.array(image, dtype=np.int16)

#Provides a visualization of some of the samples
def sample_stack(stack, rows=6, cols=6, start_with=10, show_every=None, wind_range=[0, 1]):
    if show_every==None:
      show_every = stack.shape[0]//(rows*cols)
    fig,ax = plt.subplots(rows,cols,figsize=[12,12])
    for i in range(rows*cols):
        ind = start_with + i*show_every
        ax[int(i/rows),int(i % rows)].set_title('slice %d' % ind)
        ax[int(i/rows),int(i % rows)].imshow(stack[ind],cmap='gray', vmin = wind_range[0], vmax = wind_range[1])
        ax[int(i/rows),int(i % rows)].axis('off')
    plt.show()

#Standardize the spacing between slices to 1x1x1 mm
def resample(image, scan, new_spacing=[1,1,1]):
    # Determine current pixel spacing
    actual_slice_thickeness = np.sum(
        np.array(scan[1].ImagePositionPatient) - np.array(scan[0].ImagePositionPatient))


    spacing = map(float, ([actual_slice_thickeness] + list(scan[0].PixelSpacing)))
    spacing = np.array(list(spacing))

    #Change spacing between slices to 1x1x1 mm
    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    #new_spacing = spacing / real_resize_factor

    image = scipy.ndimage.interpolation.zoom(image, real_resize_factor)

    return image, spacing

#Create mesh by returning vertices and faces data
def make_mesh(image, threshold=-300, step_size=1):
    print("Transposing surface")
    p = image.transpose(2, 1, 0)

    print("Calculating surface")
    verts, faces, norm, val = measure.marching_cubes(p, threshold, step_size=step_size, allow_degenerate=True)
    return verts, faces

#Plot in 3D
def plotly_3d(verts, faces):
    x, y, z = zip(*verts)

    # Make the colormap single color since the axes are positional not intensity.
    colormap = ['rgb(255,105,180)', 'rgb(255,255,51)', 'rgb(0,191,255)']


    fig = FF.create_trisurf(x=x,
                            y=y,
                            z=z,
                            plot_edges=False,
                            colormap=colormap,
                            simplices=faces,
                            backgroundcolor='rgb(64, 64, 64)',
                            title="Interactive Visualization")
    return plot(fig)

#Determining how far the catheter can be pushed into the ventricle without puncturing the other side
def calc_offset_ventricle_pt(kocher_point, ventricle_point, ventricle_mask, rerun=False):
    ventricle_point_backup = ventricle_point.copy()
    print('calculating ventricle point')
    offset = 0
    try_another_offset = True
    print('kocher', kocher_point)

    while offset < 30 and try_another_offset:
        print('current offset', offset, '  and ventricle point', ventricle_point)
        points = np.linspace(kocher_point, ventricle_point, 1000).astype(int)
        perf_once = False
        try_another_offset = False

        perf_pt = None
        for iii, point in enumerate(points):
            path_val = ventricle_mask[tuple(point)]
            if not perf_once and path_val:  #First time entering ventricle
                print('perforated ventricle at point', point)
                perf_once = True
                perf_pt = point.copy()
            elif perf_once and not path_val:  #Entered previously, now no longer in
                print('now outside ventricle at point', point)

                #if course of at least 15 voxels through ventricle before leaving ventricle,
                #consider two points earlier along trajectory to be bottom
                if rerun:
                    print('Course of ', np.sqrt(np.sum((perf_pt - point) ** 2)))
                    if np.sqrt(np.sum((perf_pt - point) ** 2)) > 15:
                        return tuple(points[iii - 2])
                    else:
                        offset += 1
                        ventricle_point[0] += 1
                        ventricle_point[1] += 1
                        try_another_offset = True
                        break
                else:
                    offset += 1
                    ventricle_point[0] += 1
                    ventricle_point[1] += 1
                    try_another_offset = True
                    break
            elif not perf_once and not path_val:  #Haven't hit ventricle yet, continue
                # print('still oustide')
                continue
            elif perf_once and path_val:  #Hit ventricle and still in ventricle, continue
                # print('still in')
                continue

        #Check if it even hit ventricle
        if not perf_once:
            print('did not hit ventricle')
            try_another_offset = True
            offset += 1
            ventricle_point[0] += 1
            ventricle_point[1] += 1

    if offset == 30:
        if not rerun:
            print('WARNING: Offset not able to be calculated! It will try rerun to find non-perforating course')
            return calc_offset_ventricle_pt(kocher_point, ventricle_point_backup, ventricle_mask, rerun=True)
        else:
            print('FATAL ERROR: Not able to find correct path. Please investigate.')
            return ventricle_point_backup

    print("Using offset of ", offset)
    return tuple(ventricle_point)


faces_output = None
vertices_output = None

#Download faces data
@app.route('/download_faces')
def download_faces():
    print('downloading faces')

    if faces_output is not None:
        return Response(
            faces_output.to_csv(),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=faces.csv"}
        )

#Download vertices data
@app.route('/download_vertices')
def download_vertices():
    print('downloading vertices')
    if vertices_output is not None:
        return Response(
            vertices_output.to_csv(),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=vertices.csv"}
        )

#Download trajectory data
@app.route('/download_trajectory')
def download_trajectory():
    print('downloading trajectory')
    if vertices_output is not None:
        return Response(
            trajectory_df.to_csv(),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=trajectory.csv"}
        )


#Store trajectory data
def store_trajectory(koch_pt, vent_pt, SERIES_UID):
    global trajectory_df
    if SERIES_UID:
        trajectory_df = pd.DataFrame({'points': [list(koch_pt), list(vent_pt), [1, 0, 0]]})
    else:
        trajectory_df = pd.DataFrame({'points': [list(koch_pt), list(vent_pt), [2, 0, 0]]})


#Store faces data
def store_faces_vertices(f,v):
    unity_listf = f.tolist()
    unity_listv = v.tolist()
    global faces_output
    global vertices_output

    face_dic = []
    for face in unity_listf:
        face_dic.append({"Faces":face})

    faces_output = pd.DataFrame(face_dic)

    vertex_dic = []
    for vertex in unity_listv:
        vertex_dic.append({"Vertices":vertex})

    vertices_output = pd.DataFrame(vertex_dic)

#Function for standardizing the spacing between slices to 1x1x1 mm
def resample_nrrd(image, scan_dict, new_spacing=[1, 1, 1]):
    spacing = np.diag(scan_dict["space directions"])

    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor

    image = scipy.ndimage.interpolation.zoom(image, real_resize_factor)

    return image, new_spacing

#Formula for calculating the dice score
def dice(pred, true, k=1):
    intersection = np.sum(pred[true == k]) * 2.0
    dice = intersection / (np.sum(pred) + np.sum(true))
    return dice

#Finding 3 edge points on either side of the skull
def get_edgepoints(sl_):
  conv_out = convolve2d(sl_, np.ones((3,3)), mode='same', boundary='fill', fillvalue=0)
  r, c = np.where( (conv_out>0) & (conv_out<9))
  edge_points = list(zip(r,c))
  return edge_points

#Plot the ventricles
def plotly_3d_v2(verts, faces, cmap='white'):
    x, y, z = zip(*verts)

    print("Drawing")

    #make the colormap single color since the axes are positional not intensity
    if cmap == 'white':
        colormap = ['rgb(236, 236, 212)', 'rgb(236, 236, 212)']
    else:
        colormap = ['rgb(255,105,180)', 'rgb(255,255,51)', 'rgb(0,191,255)']

    fig = FF.create_trisurf(x=x,
                            y=y,
                            z=z,
                            plot_edges=False,
                            colormap=colormap,
                            simplices=faces,
                            backgroundcolor='rgb(64, 64, 64)',
                            title="Interactive Visualization")

    return fig

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/