import sys
import os
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from vispy import app, scene
from UI_components.RHS_Components.Video_Player_Components import VideoControlWidget, VideoDepthControlWidget, VisualRepresentationWidget, ExportAndVideoScaleWidget
from utils.constants import PATH_TO_ICON_DIRECTORY

class FixedPanZoomCamera(scene.cameras.PanZoomCamera):
    def viewbox_mouse_event(self, event):
        # Ignore all mouse events to lock the video in place
        return
    

# class ImageViewer(scene.SceneCanvas):
#     def __init__(self):
#         super().__init__(keys='interactive', bgcolor='transparent')
        
#         self.unfreeze()
#         self.
        
#         view = self.central_widget.add_view(margin=0)

#         self.image = scene.visuals.Image(self.image_data, parent=view.scene, cmap='viridis')

#         view.camera = scene.PanZoomCamera(rect=(0, 0, size, size), aspect=1)
#         view.camera.set_range()
#         view.camera.interactive = False
        
#         self.freeze()

# class ColorBarWidget(scene.SceneCanvas):
#     def __init__(self):
#         super().__init__(bgcolor='transparent')
        
#         self.unfreeze()
        
#         grid = self.central_widget.add_grid(margin=0)
        
#         cmap = Colormap(['#000000', '#FF0000', '#FFFF00', '#FFFFFF'])
#         self.colorbar = scene.ColorBarWidget(cmap, orientation='right', label='Intensity', 
#                                              label_color='white')
#         grid.add_widget(self.colorbar)
#         self.colorbar.clim = (0, 1)
        
#         self.freeze()

class VideoPlayerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.buildVideoPlayerWidgets()
        # TODO: reconfigure to actually load a file
        self.loadFrames()
        self.frame_index = 0

        # Timer to update the frames
        self.timer = app.Timer('auto', connect=self.update_frame, start=False)

    def buildVideoPlayerWidgets(self):
        # Set up video player layout 
        self.mediaLayout = QVBoxLayout()
        self.mediaLayout.setContentsMargins(0, 0, 0, 0)
        self.mediaLayout.setSpacing(0)

        self.iconLayout = QHBoxLayout()
        self.iconLayout.addStretch(1)

        # Add screenshot icon
        self.screenshotIcon = QPushButton()
        self.screenshotIcon.setIcon(QIcon(os.path.join(PATH_TO_ICON_DIRECTORY, "pop.png")))
        self.screenshotIcon.setIconSize(self.screenshotIcon.sizeHint())
        self.screenshotIcon.setToolTip("Screenshot video")
        self.screenshotIcon.setFixedSize(16, 16)
        self.iconLayout.addWidget(self.screenshotIcon)
        self.mediaLayout.addLayout(self.iconLayout)


        ## EXPERIMENTAL
        self.videoPlayerLayout = QHBoxLayout()

        # Set up first SceneCanvas to show the video
        # self.videoPlayerContainer = QWidget()
        self.videoPlayerCanvas = scene.SceneCanvas(keys='interactive', bgcolor="transparent", always_on_top=True)
        # self.grid = self.vispyCanvas.central_widget.add_grid()
        # self.vispyCanvas.native.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Expand to fill space
        self.videoPlayerLayout.addWidget(self.videoPlayerCanvas.native)
        self.videoPlayerCanvas.native.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.videoPlayerCanvas.native.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.videoPlayerCanvas.native

        # QWidget.

        self.videoView = self.videoPlayerCanvas.central_widget.add_view()
        self.videoView.camera = FixedPanZoomCamera()
        self.videoView.camera.zoom_factor = 1.0  # Set initial zoom factor


        # Set up second SceneCanvas to show the colorbar
        self.colorbarCanvas = scene.SceneCanvas(keys="interactive", bgcolor="transparent")
        self.colorbarGrid = self.colorbarCanvas.central_widget.add_grid(margin=0)

        self.videoPlayerLayout.addWidget(self.colorbarCanvas.native)
        self.colorbarView = self.colorbarCanvas.central_widget.add_view()
        self.colorbarView.camera = FixedPanZoomCamera()
        self.colorbarView.camera.zoom_factor = 1.0  # Set initial zoom factor

        self.mediaLayout.addLayout(self.videoPlayerLayout)

        
        


        # # Set up Vispy canvas
        # # self.videoPlayerContainer = QWidget()
        # self.vispyCanvas = scene.SceneCanvas(keys='interactive', bgcolor=None)
        # self.vispyCanvas.size = 800, 600
        # # self.grid = self.vispyCanvas.central_widget.add_grid()
        # # self.vispyCanvas.native.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Expand to fill space
        # self.mediaLayout.addWidget(self.vispyCanvas.native)

        videoPlayerCanvasSizePolicy = QSizePolicy()



        # self.view = self.vispyCanvas.central_widget.add_view()
        # self.view.camera = FixedPanZoomCamera()
        # self.view.camera.zoom_factor = 1.0  # Set initial zoom factor


        # Initialize the rest of the widgets
        self.videoControlWidget = VideoControlWidget()
        self.visualRepresentationWidget = VisualRepresentationWidget()
        self.videoDepthControlWidget = VideoDepthControlWidget()
        self.exportAndVideoScaleWidget = ExportAndVideoScaleWidget()

        # Connect signals to slots
        self.videoControlWidget.playClicked.connect(self.playPauseVideo)
        self.videoControlWidget.skipBackClicked.connect(self.skipBackward)
        self.videoControlWidget.skipForwardClicked.connect(self.skipForward)
        self.videoControlWidget.fpsChanged.connect(self.changePlaybackRate)
        self.videoControlWidget.specificVideoFrameGiven.connect(self.goToFrameNo)
        self.videoControlWidget.videoSeekSlider.valueChanged.connect(self.setVideoPosition)
        self.videoControlWidget.videoSeekSlider.sliderReleased.connect(self.sliderReleased)

        # Fix all sizes
        self.videoControlWidget.setFixedSize(self.videoControlWidget.sizeHint())
        self.visualRepresentationWidget.setFixedSize(self.visualRepresentationWidget.sizeHint())
        self.videoDepthControlWidget.setFixedSize(self.videoDepthControlWidget.sizeHint())
        self.exportAndVideoScaleWidget.setFixedSize(self.exportAndVideoScaleWidget.sizeHint())

        # Compose all widgets
        videoControlLayout = QHBoxLayout()
        videoControlLayout.addWidget(self.videoControlWidget)
        videoControlLayout.addWidget(self.visualRepresentationWidget)
        videoControlLayout.addStretch(1)
        videoControlLayout.addWidget(self.videoDepthControlWidget)

        self.mediaLayout.addLayout(videoControlLayout)
        self.mediaLayout.addWidget(self.exportAndVideoScaleWidget)

        # Adapt the video player widget to match the size of the lower control widgets
        widthOfControlWidgets = self.videoControlWidget.width() + self.visualRepresentationWidget.width() + self.videoDepthControlWidget.width()
        # self.videoPlayerCanvas.native.
        # self.videoPlayerCanvas.native.setFixedSize(widthOfControlWidgets, widthOfControlWidgets)
        
        # Disable widgets until loadFrames is called
        self.disableWidgets()

        self.setLayout(self.mediaLayout)




    # TODO: create proper load frames func that 
    # triggers after user selects a file to open
    def loadFrames(self):
        width, height = 512, 512
        # Example: Generate random frames
        self.frames = [np.random.randint(0, 256, (height, width), dtype=np.uint8) for _ in range(100)]
        self.Image = scene.visuals.Image(self.frames[0], parent=self.videoView.scene, interpolation='nearest', cmap="plasma")
        
        
        self.colorbar = scene.ColorBarWidget(cmap="grays", orientation='right', label='Intensity', 
                                             label_color='white')
        self.colorbarGrid.add_widget(self.colorbar)
        self.colorbarCanvas.native.setFixedWidth(100)
        # self.colorbarWidget.setFixedSize(100, 400)
        

        # Create a ColorBarWidget (managed independently)
        # self.colorbar = scene.ColorBarWidget(orientation='right', cmap="plasma")
        # self.colorbar.pos = (750, 50)  # Position of the color bar within the canvas
        # self.colorbar.size = (100, 500)  # Size of the color bar
        # self.colorbar.parent = self.vispyCanvas.scene

        # self.grid.add_widget(self.colorbar)

        # Update slider with max frames
        self.videoControlWidget.videoSeekSlider.setRange(0, len(self.frames) - 1)

        # Update frame selector with max frames
        self.videoControlWidget.frameSpinBox.setRange(1, len(self.frames))

        # Enable widgets
        self.enableWidgets()
        
        # Update the view camera to fit the entire image
        self.update_view_camera()

    def disableWidgets(self):
        self.videoControlWidget.setDisabled(True)
    
    def enableWidgets(self):
        self.videoControlWidget.setEnabled(True)


###     VIDEO CONTROL FUNCTIONALITY     ###
# Following functions are for the video control widget, to play and control the video
    def update_frame(self, event):
        # Update the slider position
        self.videoControlWidget.videoSeekSlider.blockSignals(True)
        self.videoControlWidget.videoSeekSlider.setValue(self.frame_index)
        self.videoControlWidget.videoSeekSlider.blockSignals(False)

        # Update frame number
        self.videoControlWidget.frameSpinBox.blockSignals(True)
        self.videoControlWidget.frameSpinBox.setValue(self.frame_index + 1)
        self.videoControlWidget.frameSpinBox.blockSignals(False)

        # Update the image visual with the new frame
        self.Image.set_data(self.frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.videoPlayerCanvas.update()

    def update_view_camera(self):
        # Adjust the camera to fit the entire image
        img_height, img_width = self.frames[0].shape
        self.videoView.camera.set_range(x=(0, img_width), y=(0, img_height))
        self.videoView.camera.aspect = 1.0 * img_width / img_height

    def playPauseVideo(self):
        if self.timer.running:
            self.timer.stop()
            self.videoControlWidget.playIcon.setIcon(QIcon(os.path.join(PATH_TO_ICON_DIRECTORY, "play.png")))
            self.videoControlWidget.playIcon.setToolTip("Play")
        else:
            self.timer.start()
            self.videoControlWidget.playIcon.setIcon(QIcon(os.path.join(PATH_TO_ICON_DIRECTORY, "pause.png")))
            self.videoControlWidget.playIcon.setToolTip("Pause")

    def skipForward(self):
        self.frame_index = min(self.frame_index + 29, len(self.frames) - 1)  # Skip 30 frames forward
        self.update_frame(None)

    def skipBackward(self):
        self.frame_index = max(self.frame_index - 31, 0)  # Skip 30 frames backward
        self.update_frame(None)

    def changePlaybackRate(self, fps):
        self.timer.interval = 1.0 / fps

    def goToFrameNo(self, frameNo):
        if 1 <= frameNo <= len(self.frames):
            self.frame_index = frameNo - 1
            self.update_frame(None)  # Update the frame immediately

    def setVideoPosition(self, position):
        self.frame_index = position

    def sliderReleased(self):
        self.update_frame(None)

    # TODO: complete this func
    def deleteFrames(self, min, max):
        pass





# TODO: remove later
if __name__ == "__main__":
    # Path to icon directory
    ICON_DIRECTORY = "../../../assets/icons"
    PATH_TO_ICON_DIRECTORY = os.path.abspath(os.path.join(os.getcwd(), ICON_DIRECTORY))
    app = QApplication(sys.argv)
    videoPlayerWidget = VideoPlayerWidget()
    videoPlayerWidget.show()
    sys.exit(app.exec())
