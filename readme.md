<h1>GUI project for UDT data display</h1>

<p>Project of graphical user interface to display and visualize ultrasonic data</p>
It was developed as the engineer's thesis.

<h2>Description</h2>
Desktop application to efficiently visualize data obtained via ultrasound testing methods. It enables to load, preprocess and visualize data (binary files) from the chosen folder. Loaded data is stored in computer as 3D array and displayed with three 2D scans (which represent each plane of visualized array) and 1D scan (depth/amplitude plot).

<h2>Software main features</h2>
<li> pre-processing of input data: Gaussian filtration, normalization, downsampling
<li> color range and colormap customization
<li> animation of following layers along one axis
<li> additional frequency-domain filtration with result preview (inside new window)

<h2>How to run app</h2>
To run and test the program on your computer:
<li> Clone repository to your local machine.
<li> Open main.exe file inside /src folder
<li> In the shown window choose the /sample_data subfolder as the folder with data
<li> You can choose some extra options like filtering, normalizing to preprocess the data
<li> After clicking "Run" button main window should appear
<li> Recommended to uncheck both "Auto" checkboxes on the bottom side to get better results.
<li> You can try different options like setting color ranges, animation etc.

Note: In order to run application correctly, all files inside /src directory shouldn't be moved from their places after download. Otherwise, app would not run properly.

<h2>Some screenshots of application</h2>
<p><i>Loading window</i></p>
<img
  src="/img/loading-window.png"
  alt="Failed load the image">
  
<p><i>Main window</i></p>
<img
  src="/img/main-window.png"
  alt="Failed load the image">
  
<p><i>Filtering window</i></p>
<img
  src="/img/filtering-window.png"
  alt="Failed load the image">
