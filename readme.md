<h1>GUI project for UDT data display</h1>

<p>Project of graphical user interface to display and visualize data obtained via Ultrasonic Testing methods</p>

<h2>Description</h2>
Desktop application to efficiently visualize data obtained via ultrasound testing methods. It enables to load, preprocess and visualize data (stored in binary files) from the chosen folder. Loaded data is stored on computer RAM as 3D array. Inside appliaction 3 images and 1 plot are displayed. Each image represents 2D scan of visualized specimen in different planes (XY, XZ and YZ) at given position (width, height, depth) which can be adjusted by clicking any point of these images inside application window. Plot on the bottom right is single A-scan for chosen position. It shows relationship between depth and amplitude of the signal at given depth.

<h2>Aim of this project</h2>
Application was developed to enable fast visualization of ultrasonic data. With this software, user has possibility to conveniently load the data saved on disk and have a brief look on interior of examined specimen represented by 3D array.

<h2>Software main features</h2>
<li> pre-processing of input data: Gaussian filtration, normalization, downsampling
<li> color range and colormap customization
<li> animation of following layers along one of probe's axis
<li> additional frequency-domain filtration with result preview (inside new window)

<h2>Software technologies used in project</h2>
> Python
> PyQtGraph - Scientific Graphics and GUI Library for Python
> NumPy - The fundamental package for scientific computing with Python
> PyQt5 - a comprehensive set of Python bindings for Qt v5
> SciPy - Fundamental algorithms for scientific computing in Python

<h2>How to run app</h2>
To run and test the program on your computer:
<ol>
  <li> Clone repository to your local machine.
  <li> Open main.exe file inside /src folder
  <li> In the shown window choose the /sample_data subfolder as the folder with data
  <li> You can choose some extra options like filtering, normalizing to preprocess the data
  <li> To run app click the "Run" button. If entered path to folder is correct, you should see the loading bar indicating the progress of loading data into computer. Otherwise, message box with information about problem will be displayed.
  <li> If data was loaded correctly, the main window of application will appear (as shown on picture 2 in screenshots section)</li>
  <li> It is recommended to uncheck both "Auto" checkboxes on the bottom side to get better results.
  <li> Try different options like setting color ranges, playing animation etc.
</ol>

Note: In order to run application correctly, all files inside /src directory shouldn't be moved from their places after download. Otherwise, app would not run properly.

<a name="screenshots">
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
</a>
