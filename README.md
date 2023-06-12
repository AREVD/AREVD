# Automatic Segmentation and Optimal Trajectory Calculation for NeuroLens
This repository contains research artifacts for the automatic segmentation and optimal trajectory calculation section of the **2023 IEEE/ISMAR paper** “Did I Do Well? Assessment of Trainees’ Performance in Augmented Reality-assisted Neurosurgical Training” including instructions for implementation and several examples.

# Outline
1. [Overview](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#overview)
2. [Data](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#data)
3. [Implementation](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#implementation)
4. [Examples](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#examples)
5. [Citation of Dataset](https://github.com/NeuroLens6/NeuroLens/blob/main/README.md#citation-of-dataset)

ADD IN INFO ABOUT OVERVIEW

# Overview

Figure 1. Overview of Automatic Segmentation for NeuroLens

The integration of Augmented Reality (AR) in neurosurgery provides guidance to surgeons through the visualization of a patient-specific anatomy by enhancing their field of view. Our lab has developed an AR-assisted guidance system for a neurosurgical procedure, the external ventricular drain (EVD), using a marker-based tracking of a phantom model and surgical tool called NeuroLens. EVD is performed in order to alleviate pressure built in the ventricular system of the brain due to excess cerebrospinal fluid (CSF). In this procedure, surgeons drill a small hole in the skull through which they place a catheter that drains the CSF to an external closed system.

In order to make the AR system more clinically feasible, we created an automatic segmentation model in order to segment the ventricles as compared to the previous manual segmentation that took experts more than 40 minutes in the pre-operative stage. Furthermore, the algorithm also calculates the optimal trajectory of insertion of the catheter. The algorithm uses thresholding methods to segment the ventricle and optimal trajectory is calculated by estimating the starting and ending point of EVD as described by medical literature and connecting the two.

 


# Data

# Implementation

Rendering the GUI:
1. Download the code labeled “final combined segmentation.py”.
2. The user interface was created using Flask. Use the terminal to run the app and open the link provided.


Running the GUI:
Running the GUI involves filling in a set of parameters.
1. Download and save the Dicom files of the CT scans to your computer.
2. Examine the CT scans on a medical image viewing software such as Mango viewing software. If there are multiple series, choose the series corresponding to the correct window to examine the ventricles. 
3. Fill out the form using the following parameters:

	(a) **Dicom Folder Path:** This is the location of the CT scans on the computer. Insert the path based on where it has been saved on your computer.

	(b) **Series UID to Select:** Some CT scans have multiple series. This is just the ID that indicates what series to choose. If there are not multiple series, just leave it as “None”. Otherwise, select the series corresponding to the correct window to examine the ventricles. 

	(c) **Index of Which Largest Region Should be Considered the Ventricle(s):** if the largest dark region (meaning there is fluid present) present is the ventricle, set it to 0. If the ventricle is the second or third largest fluid-filled region present select 1 or 2, respectively. 

	(d) **Sensitivity of Ventricle Segmentation:** refers to the upper threshold level that users can set. Some scans have bleeds that are lighter than the ventricles, but darker than the surrounding brain area. If this is the case, set the sensitivity to low. Otherwise, set it to high.

	(e) **Degrees to rotate Up (+) and Down (-):** taking a look at the CT scan images, if they are rotated either too much up or down, this parameter can be used to correct the orientation. 

	(f) **Degrees to rotate Right (+) and Left (-):** taking a look at the CT scan images, if they are rotated either too much to the right or left, this parameter can be used to correct the orientation. 

	(g) **Iterations of Erosions and Dilations:** these are performed to confirm that the ventricles are isolated. Erosions disconnect any non-ventricle regions from the ventricles. You would perform more erosions to get more refined results that have no other non-ventricle regions connecting to the ventricles. Because the ventricles shrink slightly when erosion is performed, we use dilation to get them back to their normal size. We erode and dilate the same number of times. Too much erosion and dilation could be a problem because you can erode important parts of the ventricles. 
	
	
	(h) **Z-Index of the Nasion:** the nasion is the point on the bridge of the nose that meets the forehead. This can be found by examining the CT scans in the sagittal view and choosing the corresponding value for the Z-index.
	
	ADD IMAGE

	(i) **EVD Side:** this parameter determines if you want the EVD to come in from the right side or the left side. Usually, the EVD will come in from the right, unless there are obstructions of some sort in which the EVD will come in from the left.

	(j) **Distance (mm) to shift EVD destination Right (+) or Left (-):** Sometimes, people’s ventricles are shifted either to the left or the right. In this case, we have a parameter that allows the users to shift the final end point to the left or right by a certain number of millimeters.


# Examples
**Hydrocephalus**

Dicom Folder Path: the saved path on your computer
Series UID to Select: None
Index of Which Largest Region Should be Considered the Ventricle(s): 0
Sensitivity of Ventricle Segmentation: High
Degrees to rotate Up (+) and Down (-): 0
Degrees to rotate Right (+) and Left (-): 0
Iterations of Erosions and Dilations: 5
Z-Index of the Nasion: 33
EVD Side: Right
Distance (mm) to shift EVD destination Right (+) or Left (-): 0

![Top view of hydrocephalus](https://github.com/NeuroLens6/NeuroLens/blob/main/Hydrocephalus%20Image%201.png)
![Side view of hydrocephalus](https://github.com/NeuroLens6/NeuroLens/blob/main/Hydrocephalus%20Image%202.png)

**Middle Cerebral Artery (MCA) Stroke on Right**
Dicom Folder Path: the saved path on your computer
Series UID to Select: None
Index of Which Largest Region Should be Considered the Ventricle(s): 0
Sensitivity of Ventricle Segmentation: Low
Degrees to rotate Up (+) and Down (-): 40
Degrees to rotate Right (+) and Left (-): 0
Iterations of Erosions and Dilations: 2
Z-Index of the Nasion: 55
EVD Side: Left
Distance (mm) to shift EVD destination Right (+) or Left (-): 0

![Top view of MCA stroke](https://github.com/NeuroLens6/NeuroLens/blob/main/MCA%20Stroke%20Image%201.png) 
![Side view of MCA stroke](https://github.com/NeuroLens6/NeuroLens/blob/main/MCA%20Stroke%20Image%202.png)

**Midline Shift**
Dicom Folder Path: the saved path on your computer
Series UID to Select: None
Index of Which Largest Region Should be Considered the Ventricle(s): 0
Sensitivity of Ventricle Segmentation: High
Degrees to rotate Up (+) and Down (-): 25
Degrees to rotate Right (+) and Left (-): -8
Iterations of Erosions and Dilations: 2
Z-Index of the Nasion: 59
EVD Side: Right
Distance (mm) to shift EVD destination Right (+) or Left (-): 5

![Top view of midline shift](https://github.com/NeuroLens6/NeuroLens/blob/main/Midline%20Shift%20Image%201.png)
![Side view of midline shift](https://github.com/NeuroLens6/NeuroLens/blob/main/Midline%20Shift%20Image%202.png)

# Citation of Dataset
	@misc{rsna-intracranial-hemorrhage-detection,
   	  author = {Anouk Stein, MD, Carol Wu, Chris Carr, George Shih, Jayashree Kalpathy-Cramer, Julia Elliott, kalpathy, Luciano 		Prevedello, Marc Kohli, MD, Matt Lungren, Phil Culliton, Robyn Ball, Safwan Halabi MD},
          title = {RSNA Intracranial Hemorrhage Detection},
          publisher = {Kaggle},
          year = {2019},
          url = {https://kaggle.com/competitions/rsna-intracranial-hemorrhage-detection}
          }
