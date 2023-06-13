import logging
import os

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

DEBUG = True


#
# FreeSurferSynthStripSkullStripScripted
#

class FreeSurferSynthStripSkullStripScripted(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "FreeSurfer SynthStrip Skull Strip"
        self.parent.categories = ["Segmentation"]
        self.parent.dependencies = []
        self.parent.contributors = ["Benjamin Zwick (ISML)"]
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """Skull stripping for head studies using SynthStrip from FreeSurfer.

For a detailed description of SynthStrip please refer to its documentation <a href="https://surfer.nmr.mgh.harvard.edu/docs/synthstrip">here</a>.

See more information in <a href="https://github.com/SlicerCBM/SlicerFreeSurferCommands/tree/main/FreeSurferSynthStripSkullStripScripted/README.md">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This module uses FreeSurfer's SynthStrip command.
If you use SynthStrip in your analysis, please cite:
SynthStrip: Skull-Stripping for Any Brain Image
Andrew Hoopes, Jocelyn S. Mora, Adrian V. Dalca, Bruce Fischl*, Malte Hoffmann* (*equal contribution)
NeuroImage 260, 2022, 119474
https://doi.org/10.1016/j.neuroimage.2022.119474
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # TODO: Add sample data...


#
# FreeSurferSynthStripSkullStripScriptedWidget
#

class FreeSurferSynthStripSkullStripScriptedWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/FreeSurferSynthStripSkullStripScripted.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = FreeSurferSynthStripSkullStripScriptedLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
        self.ui.inputImageSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.outputImageSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.outputMaskSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.gpuCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.borderThresholdSliderWidget.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
        self.ui.nocsfCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)

        # Buttons
        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.GetNodeReference("InputVolume"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None and self.hasObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode):
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        # Update node selectors and sliders
        self.ui.inputImageSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
        self.ui.outputImageSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
        self.ui.outputMaskSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputMask"))
        self.ui.gpuCheckBox.checked = (self._parameterNode.GetParameter("UseGPU") == "true")
        self.ui.borderThresholdSliderWidget.value = float(self._parameterNode.GetParameter("BorderThreshold"))
        self.ui.nocsfCheckBox.checked = (self._parameterNode.GetParameter("ExcludeCSF") == "true")

        # Update buttons states and tooltips
        if self._parameterNode.GetNodeReference("InputVolume"):
            if self._parameterNode.GetNodeReference("OutputVolume"):
                self.ui.applyButton.toolTip = "Compute output stripped image volume"
                self.ui.applyButton.enabled = True
            if self._parameterNode.GetNodeReference("OutputMask"):
                self.ui.applyButton.toolTip = "Compute output binary brain mask volume"
                self.ui.applyButton.enabled = True
            if (self._parameterNode.GetNodeReference("OutputVolume") and
                self._parameterNode.GetNodeReference("OutputMask")):
                self.ui.applyButton.toolTip = "Compute output output image volume and binary brain mask volume"
                self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = "Select input and output image volume or binary brain mask volume nodes"
            self.ui.applyButton.enabled = False

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputImageSelector.currentNodeID)
        self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputImageSelector.currentNodeID)
        self._parameterNode.SetNodeReferenceID("OutputMask", self.ui.outputMaskSelector.currentNodeID)
        self._parameterNode.SetParameter("UseGPU", "true" if self.ui.gpuCheckBox.checked else "false")
        self._parameterNode.SetParameter("BorderThreshold", str(self.ui.borderThresholdSliderWidget.value))
        self._parameterNode.SetParameter("ExcludeCSF", "true" if self.ui.nocsfCheckBox.checked else "false")

        self._parameterNode.EndModify(wasModified)

    def onApplyButton(self):
        """
        Run processing when user clicks "Apply" button.
        """
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):

            # Compute output
            self.logic.process(self.ui.inputImageSelector.currentNode(),
                               self.ui.outputImageSelector.currentNode(),
                               self.ui.outputMaskSelector.currentNode(),
                               self.ui.gpuCheckBox.checked,
                               self.ui.borderThresholdSliderWidget.value,
                               self.ui.nocsfCheckBox.checked)


#
# FreeSurferSynthStripSkullStripScriptedLogic
#

class FreeSurferSynthStripSkullStripScriptedLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        if not parameterNode.GetParameter("UseGPU"):
            parameterNode.SetParameter("UseGPU", "false")
        if not parameterNode.GetParameter("BorderThreshold"):
            parameterNode.SetParameter("BorderThreshold", "1")
        if not parameterNode.GetParameter("ExcludeCSF"):
            parameterNode.SetParameter("ExcludeCSF", "false")

    def process(self, inputImageVolume,
                outputImageVolume=None, outputMaskVolume=None,
                useGPU=False, borderThreshold=1, excludeCSF=False):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        # FIXME: Update documentation
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """

        if not inputImageVolume:
            raise ValueError("Input volume is undefined")
        if not outputImageVolume and not outputMaskVolume:
            raise ValueError("Output image or mask volume is undefined")

        import time
        startTime = time.time()
        logging.info('Processing started')

        import os
        from pathlib import Path
        import qt
        # import subprocess

        temp_dir = qt.QTemporaryDir()
        temp_path = Path(temp_dir.path())
        if DEBUG:
            print("temp_path:", temp_path)

        # Temporary image files in FreeSurfer format
        temp_image = str(temp_path / 'input.mgz')
        temp_out = str(temp_path / 'stripped.mgz')
        temp_mask = str(temp_path / 'mask.mgz')
        if DEBUG:
            print(temp_image)

        # Convert image to FreeSurfer mgz format
        slicer.util.exportNode(inputImageVolume, temp_image)

        if DEBUG:
            os.listdir(temp_path)

        fs_env = os.environ.copy()
        if DEBUG:
            print(fs_env)
        # Use system Python environment
        fs_env['PYTHONHOME'] = ''
        if DEBUG:
            print("PYTHONHOME:", fs_env['PYTHONHOME'])
            print("PYTHONPATH:", fs_env['PYTHONPATH'])
        print("FREESURFER_HOME:", fs_env['FREESURFER_HOME'])

        args = [fs_env['FREESURFER_HOME'] + '/bin/mri_synthstrip']
        args.extend(['--image', temp_image])
        if outputImageVolume:
            args.extend(['--out', temp_out])
        if outputMaskVolume:
            args.extend(['--mask', temp_mask])
        if useGPU:
            args.extend(['--gpu'])
        if borderThreshold != 1:
            args.extend(['--border', str(borderThreshold)])
        if excludeCSF:
            args.extend(['--no-csf'])
        print("Command:", args)
        #subprocess.check_output(args, env=fs_env)
        proc = slicer.util.launchConsoleProcess(args)
        slicer.util.logProcessOutput(proc)

        # Load temporary files back into nodes
        if outputImageVolume:
            storage = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLVolumeArchetypeStorageNode')
            storage.SetFileName(temp_out)
            storage.ReadData(outputImageVolume)
            slicer.mrmlScene.RemoveNode(storage)
        if outputMaskVolume:
            storage = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLVolumeArchetypeStorageNode')
            storage.SetFileName(temp_mask)
            storage.ReadData(outputMaskVolume)
            slicer.mrmlScene.RemoveNode(storage)

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')


#
# FreeSurferSynthStripSkullStripScriptedTest
#

class FreeSurferSynthStripSkullStripScriptedTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_FreeSurferSynthStripSkullStripScripted1()

    def test_FreeSurferSynthStripSkullStripScripted1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # TODO: add tests...
        self.delayDisplay("This test does nothing!")

        self.delayDisplay('Test passed')
