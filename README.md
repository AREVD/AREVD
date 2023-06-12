# Automatic Segmentation and Optimal Trajectory Calculation for External Ventricular Drain
This repository contains research artifacts for the paper “Did I Do Well? Assessment of Trainees' Performance in Augmented Reality-assisted Neurosurgical Training”, submitted to **IEEE ISMAR 2023** for review including instructions of the implementation and example datasets.

# Outline
1. [Overview](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#overview)
2. [Data](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#data)
3. [Implementation](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#implementation)
4. [Examples](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#examples)
5. [Citation of Dataset](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#citation-of-dataset)

The rest of the repository is organized as follows. [Section 1](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#overview) gives a brief overview of the automatic segmentation model for NeuroLens. [Section 2](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#data) describes the data set used for this project. [Section 3](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#implementation) explains the implementation of this algorithm. [Section 4](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#examples) provides a few examples of implementation. [Section 5](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#citation-of-dataset) includes the citation of the dataset used.

# Overview

<p align="center">
  <img src="https://github.com/AREVD/AREVD/blob/main/Images/Segmenation%20Framework.png" width=50% height=50%>
</p>
<p align="center">
Figure 1. Overview of Automatic Segmentation
	</p>

The integration of Augmented Reality (AR) in neurosurgery provides guidance to surgeons through the visualization of a patient-specific anatomy by enhancing their field of view. Our lab has developed an AR-assisted guidance system for a neurosurgical procedure, the external ventricular drain (EVD), using a marker-based tracking of a phantom model and surgical tool called NeuroLens. EVD is performed in order to alleviate pressure built in the ventricular system of the brain due to excess cerebrospinal fluid (CSF). In this procedure, surgeons drill a small hole in the skull through which they place a catheter that drains the CSF to an external closed system.

In order to make the AR system more clinically feasible, we created an automatic segmentation model in order to segment the ventricles as compared to the previous manual segmentation that took experts more than 40 minutes in the pre-operative stage. Furthermore, the algorithm also calculates the optimal trajectory of insertion of the catheter. The algorithm uses thresholding methods to segment the ventricle and optimal trajectory is calculated by estimating the starting and ending point of EVD as described by medical literature and connecting the two.


# Data

The data used for this project comes from the **RSNA Intracranial Hemorrhage Detection** data set on Kaggle. This data set includes many CT scans of brains, most of which have experienced an intercranial hemorrhage or bleed in the brain.

# Implementation

## Rendering the GUI:
1. Download the code labeled “main.py” and "index.html".
2. The user interface was created using Flask. Use the terminal to run the app and open the link provided.


## Running the GUI:
Running the GUI involves filling in a set of parameters.
1. Download and save the Dicom files of the CT scans to your computer.
2. Examine the CT scans on a medical image viewing software such as Mango viewing software. If there are multiple series, choose the series corresponding to the correct window to examine the ventricles. 

**Important Note: The right and left side refer to a surgeon's view of the EVD procedure.**

<p align="center">
  <img src="https://github.com/AREVD/AREVD/blob/main/Images/Ventricles%20Image.png" width=40% height=40%>
</p>
<p align="center">
Figure 2. 
	</p>



3. Fill out the form using the following parameters:

	(a) **Dicom Folder Path:** This is the location of the CT scans on the computer. Insert the path based on where it has been saved on your computer.

	(b) **Series UID to Select:** Some CT scans have multiple series. This is just the ID that indicates what series to choose. If there are not multiple series, just leave it as “None”. Otherwise, select the series corresponding to the correct window to examine the ventricles. 

	(c) **Index of Which Largest Region Should be Considered the Ventricle(s):** if the largest dark region (meaning there is fluid present) present is the ventricle, set it to 0. If the ventricle is the second or third largest fluid-filled region present select 1 or 2, respectively. 

	(d) **Sensitivity of Ventricle Segmentation:** refers to the upper threshold level that users can set. Some scans have bleeds that are lighter than the ventricles, but darker than the surrounding brain area. If this is the case, set the sensitivity to low. Otherwise, set it to high.

	(e) **Degrees to rotate Up (+) and Down (-):** taking a look at the CT scan images, if they are rotated either too much up or down, this parameter can be used to correct the orientation. 

	(f) **Degrees to rotate Right (+) and Left (-):** taking a look at the CT scan images, if they are rotated either too much to the right or left, this parameter can be used to correct the orientation. 

	(g) **Iterations of Erosions and Dilations:** these are performed to confirm that the ventricles are isolated. Erosions disconnect any non-ventricle regions from the ventricles. You would perform more erosions to get more refined results that have no other non-ventricle regions connecting to the ventricles. Because the ventricles shrink slightly when erosion is performed, we use dilation to get them back to their normal size. We erode and dilate the same number of times. Too much erosion and dilation could be a problem because you can erode important parts of the ventricles. 
	
	
	(h) **Z-Index of the Nasion:** the nasion is the point on the bridge of the nose that meets the forehead. This can be found by examining the CT scans in the sagittal view and choosing the corresponding value for the Z-index. The scans in this dataset may look squished, but using this method to find the nasion will still work. 

<p align="center">
	<img src="https://github.com/AREVD/AREVD/blob/main/Images/Nasion%20Image%201.png" width=40% height=40%> <img src="https://github.com/AREVD/AREVD/blob/main/Images/Nasion%20Image%202.png" width=20% height=20%>
</p>

<p align="center">
Figure 3. 
	</p>

	(i) **EVD Side:** this parameter determines if you want the EVD to come in from the right side or the left side. Usually, the EVD will come in from the right, unless there are obstructions of some sort in which the EVD will come in from the left.

	(j) **Distance (mm) to shift EVD destination Right (+) or Left (-):** Sometimes, people’s ventricles are shifted either to the left or the right. In this case, we have a parameter that allows the users to shift the final end point to the left or right by a certain number of millimeters. If the ventricles are shifted too much to the right, we would also have to shift the final EVD end point to the right to make sure the catheter is targetting the correct place in the ventricle.


# Examples
## Hydrocephalus

<img src="https://github.com/AREVD/AREVD/blob/main/Images/Hydrocephalus%20Image%203.png" width=30% height=30%>

<p align="center">
Figure 4. 
	</p>

**Dicom Folder Path:** the saved path on your computer

**Series UID to Select:** None

**Index of Which Largest Region Should be Considered the Ventricle(s):** 0

**Sensitivity of Ventricle Segmentation:** High

**Degrees to rotate Up (+) and Down (-):** 8

**Degrees to rotate Right (+) and Left (-):** 0

**Iterations of Erosions and Dilations:** 5

**Z-Index of the Nasion:** 33

**EVD Side:** Right

**Distance (mm) to shift EVD destination Right (+) or Left (-):** 0


Since there is only one series, we choose a series UID of "None". The index of the largest region to be considered the ventricle would be "0" since the largest, dark continuous region corresponds to the ventricles. The sensitivity is "High" because there are no other regions that are lighter than the ventricles, but darker than the surrounding brain are. The degrees to rotate up and down would be "8" since in the saggital view of the CT scan, the skull dips downward. This positive 8 correction allows the scan to be rotated up to fix the oritentation. The degrees rotated to the right or left is "0" since the CT scan is in the correct orientation in that direction. The iterations of erosions and dilations is found by trial and error to be "5". This is the lowest number of iterations that produces a refined result without eroding away too many important features of the ventricles. The Z-index is found using the instructions earlier to be "33". Because there are no obstructions on the right side, we choose to start the EVD from the right side as that is the default. Because the ventricles aren't shifted from the midline, the distance (mm) to shift EVD distination right or left will be "0".

If these values are inputted, this output should be produced:

<img src="https://github.com/AREVD/AREVD/blob/main/Images/Hydrocephalus%20Image%201.png" width=35% height=35%> <img src="https://github.com/AREVD/AREVD/blob/main/Images/Hydrocephalus%20Image%202.png" width=40% height=40%>

<p align="center">
Figure 5. 
	</p>


## Middle Cerebral Artery (MCA) Stroke on Right

<img src="https://github.com/AREVD/AREVD/blob/main/Images/MCA%20Stroke%20Image%203.png" width=30% height=30%>

<p align="center">
Figure 6. 
	</p>


**Dicom Folder Path:** the saved path on your computer

**Series UID to Select:** None

**Index of Which Largest Region Should be Considered the Ventricle(s):** 0

**Sensitivity of Ventricle Segmentation:** Low

**Degrees to rotate Up (+) and Down (-):** 40

**Degrees to rotate Right (+) and Left (-):** 0

**Iterations of Erosions and Dilations:** 2

**Z-Index of the Nasion:** 55

**EVD Side:** Left

**Distance (mm) to shift EVD destination Right (+) or Left (-):** 0

Since there is only one series, we choose a series UID of "None". The index of the largest region to be considered the ventricle would be "0" since the largest, dark continuous region corresponds to the ventricles. The sensitivity is "Low" because there is another region that is lighter than the ventricles, but darker than the surrounding brain are. This lower value for sensitivity helps distinugish between the darker ventricle and this lighter bleed. The degrees to rotate up and down would be "40" since in the saggital view of the CT scan, the skull dips downward. This positive 40 correction allows the scan to be rotated up to fix the oritentation. The degrees rotated to the right or left is "0" since the CT scan is in the correct orientation in that direction. The iterations of erosions and dilations is found by trial and error to be "2". This is the lowest number of iterations that produces a refined result without eroding away too many important features of the ventricles. The Z-index is found using the instructions earlier to be "55". Because is the obstruction of the bleed from the right side, we choose to start the EVD from the left side. Because the ventricles aren't shifted from the midline, the distance (mm) to shift EVD distination right or left will be "0".


If these values are inputted, this output should be produced:

<img src="https://github.com/AREVD/AREVD/blob/main/Images/Final%20MCA%20Stroke%20Image%201.png" width=30% height=30%> <img src="https://github.com/AREVD/AREVD/blob/main/Images/MCA%20Stroke%20Image%202.png" width=40% height=40%>

<p align="center">
Figure 7. 
	</p>


## Midline Shift

<img src="https://github.com/AREVD/AREVD/blob/main/Images/Midline%20Shift%20Image%203.png" width=30% height=30%>

<p align="center">
Figure 8. 
	</p>


**Dicom Folder Path:** the saved path on your computer

**Series UID to Select:** None

**Index of Which Largest Region Should be Considered the Ventricle(s):** 0

**Sensitivity of Ventricle Segmentation:** High

**Degrees to rotate Up (+) and Down (-):** 25

**Degrees to rotate Right (+) and Left (-):** -8

**Iterations of Erosions and Dilations:** 2

**Z-Index of the Nasion:** 59

**EVD Side:** Right

**Distance (mm) to shift EVD destination Right (+) or Left (-):** 5

Since there is only one series, we choose a series UID of "None". The index of the largest region to be considered the ventricle would be "0" since the largest, dark continuous region corresponds to the ventricles. The sensitivity is "High" because there are no other regions that are lighter than the ventricles, but darker than the surrounding brain are. The degrees to rotate up and down would be "25" since in the saggital view of the CT scan, the skull dips downward. This positive 25 correction allows the scan to be rotated up to fix the oritentation. The degrees rotated to the right or left would be "-8" since in the axial view of the CT scan, the skull is oriented towards the right. This negative 8 correction allows the scan to be rotated towards the left to fix the oritentation. The iterations of erosions and dilations is found by trial and error to be "2". This is the lowest number of iterations that produces a refined result without eroding away too many important features of the ventricles. The Z-index is found using the instructions earlier to be "59". Because there are no obstructions on the right side, we choose to start the EVD from the right side as that is the default. Since the ventricles are shifted from the midline towards the right, the distance (mm) to shift EVD distination right or left will be "5" which is a shift of 5 mm to the right.

If these values are inputted, this output should be produced:

<img src="https://github.com/AREVD/AREVD/blob/main/Images/Midline%20Shift%20Image%201.png" width=35% height=35%> <img src="https://github.com/AREVD/AREVD/blob/main/Images/Midline%20Shift%20Image%202.png" width=35% height=35%>

<p align="center">
Figure 9. 
	</p>



# Citation of Dataset
	@misc{rsna-intracranial-hemorrhage-detection,
          title = {RSNA Intracranial Hemorrhage Detection},
          publisher = {Kaggle},
          year = {2019},
          url = {https://kaggle.com/competitions/rsna-intracranial-hemorrhage-detection}
          }
