import logging
import os

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin


#
# FreeSurferSynthSeg
#

class FreeSurferSynthSeg(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "FreeSurfer SynthSeg Brain MRI Segmentation"
        self.parent.categories = ["Segmentation"]
        self.parent.dependencies = []
        self.parent.contributors = ["Benjamin Zwick (ISML)"]
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """Segmentation of brain MRI scans using SynthSeg from FreeSurfer.

For a detailed description of SynthSeg please refer to its documentation <a href="https://surfer.nmr.mgh.harvard.edu/fswiki/SynthSeg">here</a>.

See more information in <a href="https://github.com/SlicerCBM/SlicerFreeSurferCommands/tree/main/FreeSurferSynthSeg/README.md">module documentation</a>.
"""
        self.parent.acknowledgementText = """
This module uses FreeSurfer's SynthSeg command.
If you use SynthSeg in a publication, please cite:
SynthSeg: domain randomisation for segmentation of brain MRI scans of any contrast and resolution
B. Billot, D.N. Greeve, O. Puonti, A. Thielscher, K. Van Leemput, B. Fischl, A.V. Dalca, J.E. Iglesias
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
# FreeSurferSynthSegWidget
#

class FreeSurferSynthSegWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/FreeSurferSynthSeg.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = FreeSurferSynthSegLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
        self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.outputSegmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.outputResampleSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.parcCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.robustCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.fastCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.cpuCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.threadsSpinBox.connect("valueChanged(int)", self.updateParameterNodeFromGUI)
        self.ui.v1CheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.ctCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)

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
        self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
        self.ui.outputSegmentationSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputSegmentation"))
        self.ui.outputResampleSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputResample"))
        self.ui.parcCheckBox.checked = (self._parameterNode.GetParameter("Parc") == "true")
        self.ui.robustCheckBox.checked = (self._parameterNode.GetParameter("Robust") == "true")
        self.ui.fastCheckBox.checked = (self._parameterNode.GetParameter("Fast") == "true")
        self.ui.cpuCheckBox.checked = (self._parameterNode.GetParameter("CPU") == "true")
        self.ui.threadsSpinBox.value = int(self._parameterNode.GetParameter("Threads"))
        self.ui.v1CheckBox.checked = (self._parameterNode.GetParameter("V1") == "true")
        self.ui.ctCheckBox.checked = (self._parameterNode.GetParameter("CT") == "true")

        # Update buttons states and tooltips
        if self._parameterNode.GetNodeReference("InputVolume") and self._parameterNode.GetNodeReference("OutputSegmentation"):
            self.ui.applyButton.toolTip = "Compute output volume"
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = "Select input and output volume nodes"
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

        self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
        self._parameterNode.SetNodeReferenceID("OutputSegmentation", self.ui.outputSegmentationSelector.currentNodeID)
        self._parameterNode.SetNodeReferenceID("OutputResample", self.ui.outputResampleSelector.currentNodeID)
        self._parameterNode.SetParameter("Parc", "true" if self.ui.parcCheckBox.checked else "false")
        self._parameterNode.SetParameter("Robust", "true" if self.ui.robustCheckBox.checked else "false")
        self._parameterNode.SetParameter("Fast", "true" if self.ui.fastCheckBox.checked else "false")
        self._parameterNode.SetParameter("CPU", "true" if self.ui.cpuCheckBox.checked else "false")
        self._parameterNode.SetParameter("Threads", str(self.ui.threadsSpinBox.value))
        self._parameterNode.SetParameter("V1", "true" if self.ui.v1CheckBox.checked else "false")
        self._parameterNode.SetParameter("CT", "true" if self.ui.ctCheckBox.checked else "false")

        self._parameterNode.EndModify(wasModified)

    def onApplyButton(self):
        """
        Run processing when user clicks "Apply" button.
        """
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):

            # Compute output
            self.logic.process(
                self.ui.inputSelector.currentNode(),
                self.ui.outputSegmentationSelector.currentNode(),
                self.ui.parcCheckBox.checked,
                self.ui.robustCheckBox.checked,
                self.ui.fastCheckBox.checked,
                vol=None,
                qc=None,
                post=None,
                resample=self.ui.outputResampleSelector.currentNode(),
                crop=None,
                threads=self.ui.threadsSpinBox.value,
                cpu=self.ui.cpuCheckBox.checked,
                v1=self.ui.v1CheckBox.checked,
                ct=self.ui.ctCheckBox.checked)


#
# FreeSurferSynthSegLogic
#

class FreeSurferSynthSegLogic(ScriptedLoadableModuleLogic):
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
        if not parameterNode.GetParameter("Parc"):
            parameterNode.SetParameter("Parc", "false")
        if not parameterNode.GetParameter("Robust"):
            parameterNode.SetParameter("Robust", "false")
        if not parameterNode.GetParameter("Fast"):
            parameterNode.SetParameter("Fast", "false")
        if not parameterNode.GetParameter("CPU"):
            parameterNode.SetParameter("CPU", "false")
        if not parameterNode.GetParameter("Threads"):
            parameterNode.SetParameter("Threads", "1")
        if not parameterNode.GetParameter("V1"):
            parameterNode.SetParameter("V1", "false")
        if not parameterNode.GetParameter("CT"):
            parameterNode.SetParameter("CT", "false")

    def process(self, input, output,
                parc=False, robust=False, fast=False,
                vol=None, qc=None, post=None, resample=None, crop=None,
                threads=None, cpu=False, v1=False, ct=False):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param input: input volume to be segmented
        :param output: output segmentations
        # TODO: add remaining documentation here.
        See https://surfer.nmr.mgh.harvard.edu/fswiki/SynthSeg
        """

        if not input:
            raise ValueError("Input volume is undefined")
        if not output:
            raise ValueError("Output segmentation is undefined")

        import time
        startTime = time.time()
        logging.info('Processing started')

        import os
        from pathlib import Path
        import qt

        temp_dir = qt.QTemporaryDir()
        temp_path = Path(temp_dir.path())

        # Temporary image files in FreeSurfer format
        temp_input = str(temp_path / 'input.mgz')
        temp_output = str(temp_path / 'output.mgz')
        temp_resample = str(temp_path / 'resample.mgz')

        # Convert image to FreeSurfer mgz format
        slicer.util.exportNode(input, temp_input)

        fs_env = os.environ.copy()
        # Use system Python environment
        fs_env['PYTHONHOME'] = ''
        print("FREESURFER_HOME:", fs_env['FREESURFER_HOME'])

        args = [fs_env['FREESURFER_HOME'] + '/bin/mri_synthseg']
        args.extend(['--i', temp_input])
        if output:
            args.extend(['--o', temp_output])
        if parc:
            args.extend(['--parc'])
        if robust:
            args.extend(['--robust'])
        if fast:
            args.extend(['--fast'])
        if vol:
            raise NotImplementedError
        if qc:
            raise NotImplementedError
        if post:
            raise NotImplementedError
        if resample:
            args.extend(['--resample', temp_resample])
        if crop:
            raise NotImplementedError
        if cpu:
            args.extend(['--cpu'])
            if threads:
                args.extend(['--threads', str(threads)])
        if v1:
            args.extend(['--v1'])
        if ct:
            args.extend(['--ct'])

        print("Command:", args)
        proc = slicer.util.launchConsoleProcess(args)
        slicer.util.logProcessOutput(proc)

        # Load temporary mgz images back into nodes
        if output:
            img = slicer.util.loadVolume(temp_output)
            output.CopyContent(img)
            slicer.mrmlScene.RemoveNode(img)
        if resample:
            img = slicer.util.loadVolume(temp_resample)
            resample.CopyContent(img)
            slicer.mrmlScene.RemoveNode(img)

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')


#
# FreeSurferSynthSegTest
#

class FreeSurferSynthSegTest(ScriptedLoadableModuleTest):
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
        self.test_FreeSurferSynthSeg1()

    def test_FreeSurferSynthSeg1(self):
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
