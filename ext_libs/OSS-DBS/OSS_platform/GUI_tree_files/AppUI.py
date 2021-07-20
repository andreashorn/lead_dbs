import os
import sys
import ast
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from GUI import Ui_MainWindow
import Header as Header
from pop_up_control.cpe_active import PopUpCPEActive
from pop_up_control.external_neuron_arrray import PopUpExternalNeuronArray
from pop_up_control.full_field_ifft import PopUpFullFieldIFFT
from pop_up_control.mesh_refinement import PopUpMeshRefinement
from functionalities import Functionalities
from temp_dict import Dictionary

APPLICATION_STATE = False

import subprocess
from threading import Thread


class MainWindow(Functionalities):
    def __init__(self,path_to_patient,index_side,interactive_mode,patient_folder,StimSets):
        self.main_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)

        self.path_to_patient=path_to_patient
        self.patient_folder = "'" + patient_folder + "'"
        self.index_side=int(index_side)
        self.interactive_mode=int(interactive_mode)
        self.StimSets=int(StimSets)

        self.rel_folder = self.rel_folder()

        # Add stylesheet
        self.stylesheet_filename = '{}/UX/dark.qss'.format(self.rel_folder)
        self.loadStylesheet(self.stylesheet_filename)

        self.current_file_name = " "

        # call classes
        self.externalNeuronArray = PopUpExternalNeuronArray(self.main_win)
        self.meshRefinement = PopUpMeshRefinement(self.main_win)
        self.cpeActive = PopUpCPEActive(self.main_win)
        self.fullFieldIFFT = PopUpFullFieldIFFT(self.main_win)

        # Initializations
        # Extra Widget Group Show/Hide state
        # self.ui.widget_CPE_Active.hide()
        # self.ui.widget_Global_Rot.hide()
        if self.ui.comboBox_Spectrum_Truncation_Method.currentText() == 'No Truncation':
            self.ui.widget_Spectrum_Truncation_Method.hide()

        self.ui.stackedWidget.setCurrentIndex(0)
        # self.ui.widget_Name_Prepared_Array.hide()

        # Initial States

        # Signals to slots
        # Test function
        self.ui.checkBox_Voxel_orr_DTI.stateChanged.connect(lambda: self.selection_list(self.ui.checkBox_Voxel_orr_DTI))
        self.ui.checkBox_Init_Neuron_Model_Ready.stateChanged.connect(
            lambda: self.selection_list(self.ui.checkBox_Init_Neuron_Model_Ready))
        self.ui.checkBox_Init_Mesh_Ready.stateChanged.connect(
            lambda: self.selection_list(self.ui.checkBox_Init_Mesh_Ready))
        self.ui.checkBox_Adjusted_Neuron_Model_Ready.stateChanged.connect(
            lambda: self.selection_list(self.ui.checkBox_Adjusted_Neuron_Model_Ready))
        self.ui.checkBox_Signal_Generation_Ready.stateChanged.connect(
            lambda: self.selection_list(self.ui.checkBox_Signal_Generation_Ready))
        self.ui.checkBox_CSF_Mesh_Ready.stateChanged.connect(
            lambda: self.selection_list(self.ui.checkBox_CSF_Mesh_Ready))
        self.ui.checkBox_Adapted_Mesh_Ready.stateChanged.connect(
            lambda: self.selection_list(self.ui.checkBox_Adapted_Mesh_Ready))
        self.ui.checkBox_Parallel_Computing_Ready.stateChanged.connect(
            lambda: self.selection_list(self.ui.checkBox_Parallel_Computing_Ready))
        self.ui.checkBox_Parallel_Computing_Interrupted.stateChanged.connect(
            lambda: self.selection_list(self.ui.checkBox_Parallel_Computing_Ready))
        self.ui.checkBox_IFFT_Ready.stateChanged.connect(lambda: self.selection_list(self.ui.checkBox_IFFT_Ready))

        # Page Change
        self.ui.treeWidget_Project_Browser.itemSelectionChanged.connect(lambda: self.qtree_item())
        self.ui.treeWidget_Project_Browser.topLevelItem(0).setSelected(True)

        # CheckBox signal
        self.ui.checkBox_Parallel_Computing_Interrupted.stateChanged.connect(
            lambda: self.connected_check_boxes(self.ui.checkBox_Parallel_Computing_Interrupted,
                                               self.ui.checkBox_Parallel_Computing_Ready))
        self.ui.checkBox_Parallel_Computing_Ready.stateChanged.connect(
            lambda: self.connected_check_boxes(self.ui.checkBox_Parallel_Computing_Ready,
                                               self.ui.checkBox_Parallel_Computing_Interrupted))
        self.ui.checkBox_Current_Control.stateChanged.connect(
            lambda: self.disable_widget(self.ui.checkBox_Current_Control, self.ui.checkBox_CPE_Active))

        self.ui.checkBox_Neuron_Model_Array_Prepared.stateChanged.connect(
            lambda: self.show_menu_item_on_checkbox_click(self.ui.checkBox_Neuron_Model_Array_Prepared,
                                                          self.ui.widget_Name_Of_External_Neuron_Array))
        self.ui.checkBox_Neuron_Model_Array_Prepared.stateChanged.connect(
            lambda: self.show_menu_item_on_checkbox_click(self.ui.checkBox_Neuron_Model_Array_Prepared,
                                                          self.ui.widget_Name_Of_External_Neuron_Array_2))
        self.ui.checkBox_Neuron_Model_Array_Prepared.stateChanged.connect(
            lambda: self.show_menu_item_on_checkbox_click(self.ui.checkBox_Neuron_Model_Array_Prepared,
                                                          self.ui.widget_Name_Of_External_Neuron_Array_3))
        # PopUps
        self.ui.checkBox_Neuron_Model_Array_Prepared.stateChanged.connect(
            lambda: self.pop_up_reverse(self.ui.checkBox_Neuron_Model_Array_Prepared, self.externalNeuronArray,
                                        self.main_win))
        self.ui.checkBox_Skip_Mesh_Refinement.stateChanged.connect(
            lambda: self.pop_up_reverse(self.ui.checkBox_Skip_Mesh_Refinement, self.meshRefinement, self.main_win))
        self.ui.checkBox_CPE_Active.stateChanged.connect(
            lambda: self.pop_up(self.ui.checkBox_CPE_Active, self.cpeActive, self.main_win))
        self.ui.checkBox_Full_Field_IFFT.stateChanged.connect(
            lambda: self.pop_up(self.ui.checkBox_Full_Field_IFFT, self.fullFieldIFFT, self.main_win))

        # Signal to show hidden menu items
        # self.ui.lineEdit_Brain_Shape.editingFinished.connect(lambda: self.brain_shape_name_control())
        # self.ui.lineEdit_Brain_Shape.textEdited.connect(lambda: self.brain_shape_name_control())
        # self.ui.lineEdit_Brain_Shape.textChanged.connect(lambda: self.brain_shape_name_control())

        self.ui.lineEdit_Approximating_Dimensions.editingFinished.connect(
            lambda: self.check_lineedit_if_list_entered(self.ui.lineEdit_Approximating_Dimensions.text(),
                                                        self.ui.lineEdit_Approximating_Dimensions))

        self.ui.lineEdit_Approx_Geometry_Center.editingFinished.connect(
            lambda: self.check_lineedit_if_list_entered(self.ui.lineEdit_Approx_Geometry_Center.text(),
                                                        self.ui.lineEdit_Approx_Geometry_Center))

        self.ui.comboBox_Spectrum_Truncation_Method.currentIndexChanged.connect(
            lambda: self.show_menu_item_on_combobox_state_change("No Truncation",
                                                                 self.ui.comboBox_Spectrum_Truncation_Method,
                                                                 self.ui.widget_Spectrum_Truncation_Method))
        self.ui.comboBox_Spectrum_Truncation_Method.currentIndexChanged.connect(
            lambda: self.spectrum_truncation_method_combobox_control())
        # self.ui.checkBox_Neuron_Model_Array_Prepared.stateChanged.connect(lambda: self.hide_menu_item_on_checkbox_click(self.ui.checkBox_Neuron_Model_Array_Prepared, self.externalNeuronArray.ui.widget_Global_Rot))
        self.ui.checkBox_Dimensions_From_MRI.stateChanged.connect(
            lambda: self.hide_menu_item_on_checkbox_click(self.ui.checkBox_Dimensions_From_MRI,
                                                          self.ui.widget_Approximating_Dimensions))
        self.ui.checkBox_Dimensions_From_MRI.stateChanged.connect(
            lambda: self.hide_menu_item_on_checkbox_click(self.ui.checkBox_Dimensions_From_MRI,
                                                          self.ui.widget_Approximating_Dimensions_2))
        self.ui.checkBox_Dimensions_From_MRI.stateChanged.connect(
            lambda: self.hide_menu_item_on_checkbox_click(self.ui.checkBox_Dimensions_From_MRI,
                                                          self.ui.widget_Approximating_Dimensions_3))
        self.ui.checkBox_Dimensions_From_MRI.stateChanged.connect(
            lambda: self.ui.lineEdit_Approximating_Dimensions.setText('0'))
        
        self.ui.checkBox_Approx_Geom_Centered_On_MRI.stateChanged.connect(
            lambda: self.hide_menu_item_on_checkbox_click(self.ui.checkBox_Approx_Geom_Centered_On_MRI,
                                                          self.ui.widget_Approx_Geometry_Center))
        self.ui.checkBox_Approx_Geom_Centered_On_MRI.stateChanged.connect(
            lambda: self.hide_menu_item_on_checkbox_click(self.ui.checkBox_Approx_Geom_Centered_On_MRI,
                                                          self.ui.widget_Approx_Geometry_Center_2))
        self.ui.checkBox_Approx_Geom_Centered_On_MRI.stateChanged.connect(
            lambda: self.hide_menu_item_on_checkbox_click(self.ui.checkBox_Approx_Geom_Centered_On_MRI,
                                                          self.ui.widget_Approx_Geometry_Center_3))
        self.ui.checkBox_Approx_Geom_Centered_On_MRI.stateChanged.connect(
            lambda: self.ui.lineEdit_Approx_Geometry_Center.setText('0'))

        # LineEdit to List functions
        self.ui.lineEdit_N_Ranvier.editingFinished.connect(
            lambda: self.check_lineedit_if_list_entered_absolute(self.ui.lineEdit_N_Ranvier.text(),
                                                                 self.ui.lineEdit_N_Ranvier))
        self.ui.lineEdit_Fiber_Diameter.editingFinished.connect(
            lambda: self.check_lineedit_if_list_entered_absolute(self.ui.lineEdit_Fiber_Diameter.text(),
                                                                 self.ui.lineEdit_Fiber_Diameter))
        self.ui.lineEdit_Phi_Vector.editingFinished.connect(
            lambda: self.check_lineedit_if_list_entered(self.ui.lineEdit_Phi_Vector.text(),
                                                        self.ui.lineEdit_Phi_Vector))
        self.ui.lineEdit_Truncation_Parameter.editingFinished.connect(
            lambda: self.check_lineedit_if_value_entered(self.ui.lineEdit_Truncation_Parameter.text(),
                                                         self.ui.lineEdit_Truncation_Parameter))

        # Load last saved dictionary
        self.load_last_save_state()

        # modify me!!!!!!!!!!!!!!
        self.dict_list = ["pop_up_control/dictionaries/dict_cpe_active.py",
                          "pop_up_control/dictionaries/dict_external_neuron_array.py",
                          "pop_up_control/dictionaries/dict_full_field_ifft.py",
                          "pop_up_control/dictionaries/dict_mesh_refinement.py"]

        # Display Images
        self.ui.pushButton_Placed_Neurons.clicked.connect(lambda: self.display(self.ui.label_Image_Placed_Neurons,
                                                                               self.path_to_patient+'/Images/Axon_connections.png',
                                                                               self.path_to_patient+'/Images/Placed_neurons.png'))

        self.ui.pushButton_Signal_Recovered.clicked.connect(lambda: self.display(self.ui.label_Image_Signal_Recovered,
                                                                                 self.path_to_patient+'/Images/Signal_recovered_shape.png',
                                                                                 self.path_to_patient+'/Images/Signal_recovered_shape.png'))
        self.ui.pushButton_CSF_Full_Refinement.clicked.connect(
            lambda: self.display(self.ui.label_Image_CSF_Full_Refinement,
                                 self.path_to_patient+'/Images/CSF_full_refinement.png',
                                 self.path_to_patient+'/Images/CSF_full_refinement.png'))
        self.ui.pushButton_Adapted_Mesh.clicked.connect(lambda: self.display(self.ui.label_Image_Adapted_Mesh,
                                                                             self.path_to_patient+'/Images/Adapted_mesh.png',
                                                                             self.path_to_patient+'/Images/Adapted_mesh.png'))
        self.ui.pushButton_Signal_Convoluted_1st_Point.clicked.connect(
            lambda: self.display(self.ui.label_Image_Signal_Convoluted_1st_Point,
                                 self.path_to_patient+'/Images/Signal_convoluted_1st_point.png',
                                 self.path_to_patient+'/Images/Signal_convoluted_1st_point.png'))
        self.ui.pushButton_Axon_Activation.clicked.connect(lambda: self.display(self.ui.label_Image_Axon_Activation,
                                                                                self.path_to_patient+'/Images/Axon_activation.png',
                                                                                self.path_to_patient+'/Images/Activated_neurons.png'))

        # Load/Save/Reset/Run to dictionary
        self.ui.pushButton_Run.clicked.connect(lambda: self.dict_write(self.output_dict(), self.current_file_name))
        # Modification to run a subprocess on another thread when Run button is clicked.
        self.ui.pushButton_Run.clicked.connect(lambda: self.run_thread())

        self.ui.pushButton_SaveAs.clicked.connect(lambda: self.save_as())
        self.ui.pushButton_Load.clicked.connect(lambda: self.load_dict())
        self.ui.pushButton_Reset.clicked.connect(lambda: self.reset_state())

    def show(self):
        self.main_win.show()
        if not self.interactive_mode:
            self.save_as(os.path.join(os.path.abspath(os.getcwd()),'GUI_inp_dict.py'))
            self.run_thread()

    def run_command(self):
        """The subprocess takes the terminal command as a list."""
        #put a command for the "Run" button in the GUI. The command depends on whether you use Docker or not. In the former case, you have two different options: as a sudo user or not. Check the tutorial.
        dir_code=os.path.dirname(os.getcwd()) # OSS-DBS folder to be mount, NOT OSS_platform folder
        if sys.platform=='linux':
            if os.environ.get('SINGULARITY_NAME'):
                output = subprocess.run(['python3', 'Launcher_OSS_lite.py'])
            else:
                output = subprocess.run(
                    ['docker', 'run', '-e', 'PATIENTDIR', '--volume', dir_code + ':/opt/OSS-DBS',
                     '--volume', self.path_to_patient + ':/opt/Patient',
                     '-it', '--rm', 'custom_oss-dbs', 'python3', 'Launcher_OSS_lite.py'])  #
        elif sys.platform == 'darwin' or sys.platform=='win32':
            output = subprocess.run(
                ['docker', 'run', '-e', 'PATIENTDIR', '--volume', dir_code + ':/opt/OSS-DBS',
                '--volume', self.path_to_patient + ':/opt/Patient',
                '-it', '--rm', 'ningfei/oss-dbs', 'python3', 'Launcher_OSS_lite.py'])
        else:
            print("The system's OS does not support OSS-DBS")
            raise SystemExit

        # does not work on macOS
        #out2 = subprocess.run(['docker','logs','OSS_container'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  #
        #stdout_as_str = out2.stdout.decode("utf-8")

        #text_file = open(self.path_to_patient+"/Docker_log.txt", "wt")
        #n = text_file.write(stdout_as_str)
        #text_file.close()

        #print(output.returncode)

        #if not os.path.exists(self.path_to_patient+'/success.txt'):
        #    subprocess.call(['touch', self.path_to_patient+'/fail.txt'])
        #    print("Error occurred, check the terminal")
        #else:
        #    print("Simulation is completed")
        #    self.closeWindow()

        if self.index_side==0:
            if not os.path.exists(self.path_to_patient+'/success_rh.txt'):
                subprocess.call(['touch', self.path_to_patient+'/fail_rh.txt'])
                print("Error occurred when simulating rh, check the terminal")
                if sys.platform!='linux':
                    self.closeWindow()
            else:
                print("Simulation is completed")
                self.closeWindow()
        else:
            if not os.path.exists(self.path_to_patient+'/success_lh.txt'):
                subprocess.call(['touch', self.path_to_patient+'/fail_lh.txt'])
                print("Error occurred when simulating lh, check the terminal")
                if sys.platform!='linux':
                    self.closeWindow()
            else:
                print("Simulation is completed")
                self.closeWindow()

        self.closeWindow()
        # the commands below work only with a properly installed Paraview (supporting from paraview.simple import *)

        #print(self.path_to_patient)
        #prepare screenshots
        #we need to insert the correct path here (use the already written python scripts)
        #with open(os.devnull, 'w') as FNULL: subprocess.call(['python','Visualization_files/Paraview_csv_neurons.py',self.path_to_patient], shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

        # try:
        #     subprocess.run(['python','Visualization_files/Paraview_csv_neurons.py',self.path_to_patient])
        # except:
        #     subprocess.run(['python','Visualization_files/Paraview_connections_processed.py',self.path_to_patient])

        # try:
        #     subprocess.run(['python','Visualization_files/Paraview_csv_activation.py.py',self.path_to_patient])
        # except:
        #     subprocess.run(['python','Visualization_files/Paraview_connections_activation.py',self.path_to_patient])

        # subprocess.run(['python','Visualization_files/Paraview_CSFref.py',self.path_to_patient])
        # subprocess.run(['python','Visualization_files/Paraview_adapted.py',self.path_to_patient])

        #subprocess.run(['python','Visualization_files/Paraview_csv_neurons.py',self.path_to_patient])

        #subprocess.run(['xterm','-hold','-e','ls'])
        #command_to_run='gnome-terminal -- bash -c "python3 Launcher_OSS_lite.py && read"'
        #command_to_run='xterm -hold -e python3 Launcher_OSS_lite.py'
        #subprocess.run(['xterm','-hold','-e','python3','Launcher_OSS_lite.py'])
        #subprocess.run(['gnome-terminal','--execute','python3', 'Launcher_OSS_lite.py'])#
        #substitute tilda
        #subprocess.run([
        """add the command you use to run OSS-DBS here (as shown above)"""


    def run_thread(self):
        t = Thread(target=self.run_command)
        t.start()

    # Call to tree Item
    def qtree_item(self):
        if self.ui.treeWidget_Project_Browser.topLevelItem(0).isSelected():
            self.click_change_page(0)
        elif self.ui.treeWidget_Project_Browser.topLevelItem(1).isSelected():
            self.click_change_page(1)
        elif self.ui.treeWidget_Project_Browser.topLevelItem(2).isSelected():
            self.click_change_page(2)
        elif self.ui.treeWidget_Project_Browser.topLevelItem(5).isSelected():
            self.click_change_page(3)
        elif self.ui.treeWidget_Project_Browser.topLevelItem(6).isSelected():
            self.click_change_page(4)
        elif self.ui.treeWidget_Project_Browser.topLevelItem(7).isSelected():
            self.click_change_page(5)
        elif self.ui.treeWidget_Project_Browser.topLevelItem(8).isSelected():
            self.click_change_page(6)

    def click_change_page(self, page_num):
        self.ui.stackedWidget.setCurrentIndex(page_num)

    def spectrum_truncation_method_combobox_control(self):

        if self.ui.comboBox_Spectrum_Truncation_Method.currentText() == 'Octave Band Method':
            self.ui.widget_STM_1.show()
            self.ui.widget_STM_2.show()
            self.ui.widget_STM_3.show()
            self.ui.widget_STM_4.hide()
            self.ui.widget_STM_5.hide()
            self.ui.widget_STM_6.hide()
            self.ui.widget_Truncate_Already_Obtained_Full_Solution.hide()
            self.ui.widget_Truncate_Already_Obtained_Full_Solution_2.hide()
            self.ui.widget_Truncate_Already_Obtained_Full_Solution_3.hide()
        else:
            self.ui.widget_STM_1.hide()
            self.ui.widget_STM_2.hide()
            self.ui.widget_STM_3.hide()
            self.ui.widget_STM_4.show()
            self.ui.widget_STM_5.show()
            self.ui.widget_STM_6.show()
            self.ui.widget_Truncate_Already_Obtained_Full_Solution.show()
            self.ui.widget_Truncate_Already_Obtained_Full_Solution_2.show()
            self.ui.widget_Truncate_Already_Obtained_Full_Solution_3.show()

    # Selection list
    def selection_list(self, checkbox):
        vmri = self.ui.checkBox_Voxel_orr_MRI
        vdti = self.ui.checkBox_Voxel_orr_DTI
        inmr = self.ui.checkBox_Init_Neuron_Model_Ready
        imr = self.ui.checkBox_Init_Mesh_Ready
        anmr = self.ui.checkBox_Adjusted_Neuron_Model_Ready
        sgr = self.ui.checkBox_Signal_Generation_Ready
        cmr = self.ui.checkBox_CSF_Mesh_Ready
        amr = self.ui.checkBox_Adapted_Mesh_Ready
        pcr = self.ui.checkBox_Parallel_Computing_Ready
        pci = self.ui.checkBox_Parallel_Computing_Interrupted
        ifftr = self.ui.checkBox_IFFT_Ready

        full_checkbox_list = [vmri, vdti, inmr, anmr, sgr, cmr, amr, pcr, pci, ifftr]

        vdti_L = [vmri]
        inmr_L = [vmri]
        imr_L = [vmri, inmr]
        anmr_L = [vmri, inmr, imr]
        sgr_L = [pcr, pci, ifftr]
        cmr_L = [vmri, inmr, imr, anmr, sgr]
        amr_L = [vmri, inmr, imr, anmr, cmr, sgr]
        pcr_L = [vmri, inmr, imr, anmr, cmr, amr, sgr]
        pci_L = [vmri, inmr, imr, anmr, cmr, amr, sgr]
        ifftr_L = [vmri, inmr, imr, anmr, cmr, amr, sgr, pcr]

        if checkbox == vdti:
            if checkbox.checkState() == 2:
                for x in vdti_L:
                    if x.checkState() == 0:
                        x.setCheckState(2)

        if checkbox == inmr:
            if checkbox.checkState() == 2:
                for x in inmr_L:
                    if x.checkState() == 0:
                        x.setCheckState(2)

        elif checkbox == imr:
            if checkbox.checkState() == 2:
                for x in imr_L:
                    if x.checkState() == 0:
                        x.setCheckState(2)

        elif checkbox == anmr:
            if checkbox.checkState() == 2:
                for x in anmr_L:
                    if x.checkState() == 0:
                        x.setCheckState(2)

        elif checkbox == cmr:
            if checkbox.checkState() == 2:
                for x in cmr_L:
                    if x.checkState() == 0:
                        x.setCheckState(2)

        elif checkbox == amr:
            if checkbox.checkState() == 2:
                for x in amr_L:
                    if x.checkState() == 0:
                        x.setCheckState(2)

        elif checkbox == sgr:
            if checkbox.checkState() == 0:
                for x in sgr_L:
                    x.setCheckState(0)

        elif checkbox == pcr:
            if checkbox.checkState() == 2:
                for x in pcr_L:
                    if x.checkState() == 0:
                        x.setCheckState(2)

        elif checkbox == pci:
            if checkbox.checkState() == 2:
                for x in pci_L:
                    if x.checkState() == 0:
                        x.setCheckState(2)

        elif checkbox == ifftr:
            if checkbox.checkState() == 2:
                pcr.setCheckState(2)
                pci.setCheckState(0)
                for x in ifftr_L:
                    if x.checkState() == 0:
                        x.setCheckState(2)

    def output_dict(self):
        # from pop_up_control.dictionaries import dict_cpe_active, dict_external_neuron_array, dict_full_field_ifft, \
        #     dict_mesh_refinement
        output_dict = Dictionary(self).output_dict()
        output_dict['patient_folder'] = self.patient_folder
        output_dict['Stim_side'] = self.index_side
        output_dict['stretch'] = self.stretch
        output_dict['StimSets'] = self.StimSets

        # # concatenate various dictionaries
        # output_dict.update(dict_cpe_active.d)
        # output_dict.update(dict_external_neuron_array.d)
        # output_dict.update(dict_full_field_ifft.d)
        # output_dict.update(dict_mesh_refinement.d)

        return output_dict

    def dict_write(self, output_dict, filename):

        if os.path.isabs(filename):
            pass
        else:
            filename = '{}/{}'.format(self.rel_folder, filename)

        if " " in filename or "default_dict.py" in filename or "last_save.py" in filename:
            self.save_as()
        else:
            with open(filename, 'w') as test_dict:
                test_dict.write(Header.header)
                test_dict.write("d = {\n")

                for x in output_dict:
                    test_dict.write("    '{}': {},\n".format(x, output_dict[x]))

                # append data from other dicts
                for dict_filename in self.dict_list:
                    dict_filename = '{}/{}'.format(self.rel_folder, dict_filename)
                    with open(dict_filename, 'r') as f:
                        content = f.read().split('{')[1].split('}')[0]
                        test_dict.write(content.strip())

                test_dict.write("}\n")

            with open("{}/GUI_tree_files/last_save.py".format(self.rel_folder), 'w') as last_save:
                last_save.write("d = {\n")
                for x in output_dict:
                    last_save.write("    '{}': {},\n".format(x, output_dict[x]))
                last_save.write("    }\n")

            if self.interactive_mode:
                self.info("Run", "Setup state has been written to {}.".format(filename))
            else:
                print("Setup state has been written to {}".format(filename))

    def save_as(self, filename=""):
        if filename == "":
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            filename, _ = QFileDialog.getSaveFileName(None, "Save State", "",
                                                      "All Files (*);;Text Files (*.txt)", options=options)

        if filename != "":
            filename = self.py_check(filename)
            if "default_dict.py" in filename or "last_save.py" in filename:
                self.info("Write Forbidden",
                          "Oops, that didn't save! It seems you attempted to write to the default dictionary.")
            else:
                with open(filename, 'w') as save_as_dict:
                    save_as_dict.write(Header.header)
                    save_as_dict.write("d = {\n")
                    for x in self.output_dict():
                        save_as_dict.write("    '{}': {},\n".format(x, self.output_dict()[x]))

                    # append data from other dicts
                    for dict_filename in self.dict_list:
                        dict_filename = '{}/{}'.format(self.rel_folder, dict_filename)
                        with open(dict_filename, 'r') as f:
                            content = f.read().split('{')[1].split('}')[0]
                            save_as_dict.write(content.strip())

                    save_as_dict.write("}\n")

                with open("{}/GUI_tree_files/last_save.py".format(self.rel_folder), 'w') as last_save:
                    last_save.write("d = {\n")
                    for x in self.output_dict():
                        last_save.write("    '{}': {},\n".format(x, self.output_dict()[x]))

                    # append data from other dicts
                    for dict_filename in self.dict_list:
                        dict_filename = '{}/{}'.format(self.rel_folder, dict_filename)
                        with open(dict_filename, 'r') as f:
                            content = f.read().split('{')[1].split('}')[0]
                            last_save.write(content.strip())

                    last_save.write("}\n")

                if self.interactive_mode:
                    self.info("Run", "Setup state has been written to {}.".format(filename))
                else:
                    print("Setup state has been written to {}".format(filename))
                self.set_current_file_name(filename)

    def set_load_state(self, d):
        self.stretch=d['stretch']

        # default choice of processors
        if sys.platform=='linux':
            physical_cores=os.popen("""lscpu -b -p=Core,Socket | grep -v '^#' | sort -u | wc -l""").read()[:-1]
            d['number_of_processors']=int(int(physical_cores)*0.5)     # leave some
            print("Number of cores drawn by default: ",d['number_of_processors'])
        else:
            print("All cores available for Docker will be drawn")

        self.ui.checkBox_Voxel_orr_MRI.setCheckState(self.anti_corrector(d['voxel_arr_MRI']))
        self.ui.checkBox_Voxel_orr_DTI.setCheckState(----self.anti_corrector(d['voxel_arr_DTI']))
        self.ui.checkBox_Init_Neuron_Model_Ready.setCheckState(self.anti_corrector(d['Init_neuron_model_ready']))
        self.ui.checkBox_Init_Mesh_Ready.setCheckState(self.anti_corrector(d['Init_mesh_ready']))
        self.ui.checkBox_Adjusted_Neuron_Model_Ready.setCheckState(
            self.anti_corrector(d['Adjusted_neuron_model_ready']))
        self.ui.checkBox_CSF_Mesh_Ready.setCheckState(self.anti_corrector(d['CSF_mesh_ready']))
        self.ui.checkBox_Adapted_Mesh_Ready.setCheckState(self.anti_corrector(d['Adapted_mesh_ready']))
        self.ui.checkBox_Signal_Generation_Ready.setCheckState(self.anti_corrector(d['signal_generation_ready']))
        self.ui.checkBox_Parallel_Computing_Ready.setCheckState(self.anti_corrector(d['Parallel_comp_ready']))
        self.ui.checkBox_Parallel_Computing_Interrupted.setCheckState(
            self.anti_corrector(d['Parallel_comp_interrupted']))
        self.ui.checkBox_IFFT_Ready.setCheckState(self.anti_corrector(d['IFFT_ready']))
        self.ui.lineEdit_MRI_Data_Name.setText(d['MRI_data_name'])
        self.ui.checkBox_MRI_m.setCheckState(self.anti_corrector(d['MRI_in_m']))
        self.ui.lineEdit_DTI_Data_Name.setText(d['DTI_data_name'])
        self.ui.checkBox_DTI_m.setCheckState(self.anti_corrector(d['DTI_in_m']))
        self.ui.doubleSpinBox_CSF_Index.setValue(d['CSF_index'])
        self.ui.doubleSpinBox_WM_Index.setValue(d['WM_index'])
        self.ui.doubleSpinBox_GM_Index.setValue(d['GM_index'])
        self.ui.comboBox_Default_Material.setCurrentIndex(d['default_material'] - 1)
        self.ui.comboBox_Electrode_Type.setCurrentText(d['Electrode_type'])
        self.ui.lineEdit_Brain_Shape.setText("{}".format(d['Brain_shape_name']))
        # self.ui.doubleSpinBox_X_Length.setValue(d['x_length'])
        # self.ui.doubleSpinBox_Y_Length.setValue(d['y_length'])
        # self.ui.doubleSpinBox_Z_Length.setValue(d['z_length'])
        self.get_lineedit_entry(d['Aprox_geometry_center'], self.ui.lineEdit_Approx_Geometry_Center)
        try:
            self.get_lineedit_entry(d['Approximating_Dimensions'], self.ui.lineEdit_Approximating_Dimensions)
        except:
            pass

        self.ui.doubleSpinBox_Implantation_Coordinate_X.setValue(d['Implantation_coordinate_X'])
        self.ui.doubleSpinBox_Implantation_Coordinate_Y.setValue(d['Implantation_coordinate_Y'])
        self.ui.doubleSpinBox_Implantation_Coordinate_Z.setValue(d['Implantation_coordinate_Z'])
        self.ui.doubleSpinBox_2nd_Point_On_Lead_X.setValue(d['Second_coordinate_X'])
        self.ui.doubleSpinBox_2nd_Point_On_Lead_Y.setValue(d['Second_coordinate_Y'])
        self.ui.doubleSpinBox_2nd_Point_On_Lead_Z.setValue(d['Second_coordinate_Z'])
        self.ui.doubleSpinBox_Turn_Around_Lead_Axis.setValue(d['Rotation_Z'])
        self.ui.doubleSpinBox_Encapsulation_Thickness.setValue(d['encap_thickness'])
        self.ui.comboBox_Encapsulation_Tissue_Type.setCurrentIndex(d['encap_tissue_type'] - 1)
        self.ui.doubleSpinBox_Conductivity_Scaling.setValue(d['encap_scaling_cond'])
        self.ui.doubleSpinBox_Permittivity_Scaling.setValue(d['encap_scaling_perm'])
        self.ui.lineEdit_Pattern_Model_Name.setText("{}".format(d['pattern_model_name']))
        try:
            self.ui.comboBox_Axon_Model_Type.setCurrentText("{}".format(d['Axon_Model_Type']))
        except:
            pass
        self.ui.lineEdit_Fiber_Diameter.setText("{}".format(d['diam_fib']))
        self.ui.lineEdit_N_Ranvier.setText("{}".format(d['n_Ranvier']))
        self.ui.doubleSpinBox_V_Init.setValue(d['v_init'])
        self.ui.checkBox_Neuron_Model_Array_Prepared.setCheckState(
            self.anti_corrector(d['Neuron_model_array_prepared']))
        self.ui.lineEdit_Name_Prepared_Neuron_Array.setText("{}".format(d['Name_prepared_neuron_array']))
        self.externalNeuronArray.ui.checkBox_Global_Rot.setCheckState(self.anti_corrector(d['Global_rot']))
        if self.externalNeuronArray.ui.checkBox_Global_Rot.checkState() == 2:
            self.externalNeuronArray.ui.doubleSpinBox_X_Seed.setValue(d['x_seed'])
            self.externalNeuronArray.ui.doubleSpinBox_Y_Seed.setValue(d['y_seed'])
            self.externalNeuronArray.ui.doubleSpinBox_Z_Seed.setValue(d['z_seed'])
            self.externalNeuronArray.ui.spinBox_X_Steps.setValue(d['x_steps'])
            self.externalNeuronArray.ui.spinBox_Y_Steps.setValue(d['y_steps'])
            self.externalNeuronArray.ui.spinBox_Z_Steps.setValue(d['z_steps'])
            self.externalNeuronArray.ui.doubleSpinBox_X_Step.setValue(d['x_step'])
            self.externalNeuronArray.ui.doubleSpinBox_Y_Step.setValue(d['y_step'])
            self.externalNeuronArray.ui.doubleSpinBox_Z_Step.setValue(d['z_step'])
            self.get_lineedit_entry(d['alpha_array_glob'], self.externalNeuronArray.ui.lineEdit_Alpha_Array_Glob)
            self.get_lineedit_entry(d['beta_array_glob'], self.externalNeuronArray.ui.lineEdit_Beta_Array_Glob)
            self.get_lineedit_entry(d['gamma_array_glob'], self.externalNeuronArray.ui.lineEdit_Gamma_Array_Glob)
        else:
            self.get_lineedit_entry(d['X_coord_old'], self.externalNeuronArray.ui.lineEdit_X_Coordinate_Old)
            self.get_lineedit_entry(d['Y_coord_old'], self.externalNeuronArray.ui.lineEdit_Y_Coordinate_Old)
            self.get_lineedit_entry(d['Z_coord_old'], self.externalNeuronArray.ui.lineEdit_Z_Coordinate_Old)
            self.get_lineedit_entry(d['YZ_angles'], self.externalNeuronArray.ui.lineEdit_YZ_Angles)
            self.get_lineedit_entry(d['ZX_angles'], self.externalNeuronArray.ui.lineEdit_ZX_Angles)
            self.get_lineedit_entry(d['XY_angles'], self.externalNeuronArray.ui.lineEdit_XY_Angles)

        self.ui.comboBox_Laplace_Formulation.setCurrentText(d['EQS_core'])
        self.ui.checkBox_Skip_Mesh_Refinement.setCheckState(self.anti_corrector(d['Skip_mesh_refinement']))
        self.get_lineedit_entry(d['refinement_frequency'], self.meshRefinement.ui.lineEdit_Refinement_Frequency)
        self.meshRefinement.ui.spinBox_No_Of_Refinement_Frequencies.setValue(d['num_ref_freqs'])
        self.meshRefinement.ui.doubleSpinBox_Deviation_Threshold.setValue(d['Adaptive_frac_div'])
        self.meshRefinement.ui.doubleSpinBox_Min_Scaling.setValue(d['Min_Scaling'])
        self.meshRefinement.ui.doubleSpinBox_CSF_Ref_Reg.setValue(d['CSF_ref_reg'])
        self.meshRefinement.ui.doubleSpinBox_Rel_Div.setValue(d['rel_div'])
        self.meshRefinement.ui.doubleSpinBox_Rel_Div_Current.setValue(d['rel_div_current'])
        self.ui.spinBox_El_Order.setValue(d['el_order'])
        self.ui.spinBox_Number_Of_Processors.setValue(d['number_of_processors'])
        try:
            self.ui.checkBox_FEniCS_MPI.setCheckState(self.anti_corrector(d['FEniCS_MPI']))
        except:
            pass
        self.ui.checkBox_Current_Control.setCheckState(self.anti_corrector(d['current_control']))
        self.get_lineedit_entry(d['Phi_vector'], self.ui.lineEdit_Phi_Vector)
        try:
            self.ui.comboBox_Solver_Type.setCurrentText("{}".format(d['Solver_Type']))
        except:
            pass
        self.ui.doubleSpinBox_Frequency.setValue(d['freq'])
        self.ui.doubleSpinBox_T.setValue(d['T'])
        self.ui.doubleSpinBox_T_Step.setValue(d['t_step'])
        self.ui.doubleSpinBox_Signal_Shift.setValue(d['phi'])
        self.ui.comboBox_Signal_Type.setCurrentText("{}".format(d['Signal_type']))
        self.ui.doubleSpinBox_Amplitude_Scale.setValue(d['Ampl_scale'])
        self.ui.checkBox_CPE_Active.setCheckState(self.anti_corrector(d['CPE_activ']))
        self.cpeActive.ui.doubleSpinBox_Alpha.setValue(d['beta'])
        self.cpeActive.ui.doubleSpinBox_K_S.setValue(d['K_A'])
        self.cpeActive.ui.doubleSpinBox_Alpha_Ground.setValue(d['beta_ground'])
        self.cpeActive.ui.doubleSpinBox_K_S_Ground.setValue(d['K_A_ground'])
        self.ui.checkBox_Full_Field_IFFT.setCheckState(self.anti_corrector(d['Full_Field_IFFT']))
        self.fullFieldIFFT.ui.spinBox_T_Step_End.setValue(d['t_step_end'])
        self.fullFieldIFFT.ui.checkBox_VTA_From_DivE.setCheckState(self.anti_corrector(d['VTA_from_divE']))
        self.fullFieldIFFT.ui.checkBox_VTA_From_NEURON.setCheckState(self.anti_corrector(d['VTA_from_NEURON']))
        self.fullFieldIFFT.ui.checkBox_VTA_From_E.setCheckState(self.anti_corrector(d['VTA_from_E']))
        self.get_lineedit_entry(d['Activation_threshold_VTA'], self.fullFieldIFFT.ui.lineEdit_Activation_Threshold)

        self.ui.comboBox_Spectrum_Truncation_Method.setCurrentText(d['spectrum_trunc_method'])

        self.get_entry_truncation_parameter(d['trunc_param'], self.ui.comboBox_Spectrum_Truncation_Method,
                                            self.ui.lineEdit_Truncation_Parameter, self.ui.spinBox_Truncation_Parameter)

        self.ui.checkBox_Truncate_The_Obtained_Full_Solution.setCheckState(
            self.anti_corrector(d['Truncate_the_obtained_full_solution']))
        #self.ui.checkBox_Show_Paraview_Screenshots.setCheckState(self.anti_corrector(d['Show_paraview_screenshots']))

        self.ui.checkBox_external_grounding.setCheckState(self.anti_corrector(d['external_grounding']))

        # save sub dictionaries
        self.cpeActive.saveDict()
        self.meshRefinement.saveDict()
        self.fullFieldIFFT.saveDict()
        self.externalNeuronArray.saveDict()

    def load_dict(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        filename, _ = QFileDialog.getOpenFileName(None, "Load State", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if filename:
            with open(filename, 'r') as f:
                num = f.read().find('{')
                f.seek(num)
                content = f.read()
                d = ast.literal_eval(content.strip())
                self.set_load_state(d)

            self.info("Run", "{} has been loaded successfully.".format(filename))
            self.set_current_file_name(filename)

    def reset_state(self):
        filename = "{}/GUI_tree_files/default_dict.py".format(self.rel_folder)
        with open(filename, 'r') as f:
            num = f.read().find('{')
            f.seek(num)
            content = f.read()
            d = ast.literal_eval(content.strip())
            self.set_load_state(d)
        # self.set_current_file_name(filename)

        # Display Images
        self.display(self.ui.label_Image_Placed_Neurons,
                     '{}/icons/image_placeholder.png'.format(self.rel_folder),
                     '{}/icons/image_placeholder.png'.format(self.rel_folder), 2)
        self.display(self.ui.label_Image_Signal_Recovered,
                     '{}/icons/image_placeholder.png'.format(self.rel_folder),
                     '{}/icons/image_placeholder.png'.format(self.rel_folder), 2)
        self.display(self.ui.label_Image_CSF_Full_Refinement,
                     '{}/icons/image_placeholder.png'.format(self.rel_folder),
                     '{}/icons/image_placeholder.png'.format(self.rel_folder), 2)
        self.display(self.ui.label_Image_Adapted_Mesh,
                     '{}/icons/image_placeholder.png'.format(self.rel_folder),
                     '{}/icons/image_placeholder.png'.format(self.rel_folder), 2)
        self.display(self.ui.label_Image_Signal_Convoluted_1st_Point,
                     '{}/icons/image_placeholder.png'.format(self.rel_folder),
                     '{}/icons/image_placeholder.png'.format(self.rel_folder), 2)
        self.display(self.ui.label_Image_Axon_Activation, '{}/icons/image_placeholder.png'.format(self.rel_folder),
                     '{}/icons/image_placeholder.png'.format(self.rel_folder), 2)

    def load_last_save_state(self):
        try:
            filename = "{}/GUI_tree_files/default_dict.py".format(self.rel_folder)
            with open(filename, 'r') as f:
                num = f.read().find('{')
                f.seek(num)
                content = f.read()
                d = ast.literal_eval(content.strip())
                self.set_load_state(d)
            # self.info("Run", "Last save state was loaded successfully")
            # self.set_current_file_name(filename)
        except AssertionError:
            # self.info("Run", "Oopsie! There seems to have been a problem with loading the default settings")
            pass
        except ValueError:
            # self.info("Run", "Oopsie! There seems to have been a problem with loading the default settings")
            pass

        except SyntaxError:
            # self.info("Run", "Oopsie! There seems to be a syntax error with the last saved dictionary file.")
            pass

        except FileNotFoundError:
            self.info("Run", "Oopsie! A default_dict.py file seems not to be found.")
            pass
        except:
            self.info("Run", "Oopsie! There seems to have been a problem loading the last saved dictionary.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow(*sys.argv[1:])
    main_win.show()
    sys.exit(app.exec_())
