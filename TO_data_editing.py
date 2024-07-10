"""
/***************************************************************************
  TO_data_editing.py

  QGIS plugin do edycji danych oświetlenia (TO).
  --------------------------------------
  Start work date : 05.06.2024
  Copyright: (C) 2024 by Piotr Michałowski
  Email: piotrm35@hotmail.com
/***************************************************************************
"""


SCRIPT_TITLE = 'TO_data_editing'
SCRIPT_NAME = 'TO_data_editing'
SCRIPT_VERSION = '0.1.0'
GENERAL_INFO = """
author: Piotr Michałowski, Olsztyn, woj. W-M, Poland
piotrm35@hotmail.com
"""


#====================================================================================================================
# Setup:


LOGGER = True
MANUAL_FILE_NAME = 'TO_data_editing_MANUAL.pdf'
PATH_TO_ATTACHMENTS_FOLDER = 'E:\\TO_img'
PATH_TO_REMOVED_ATTACHMENTS_FOLDER = 'E:\\TO_img_REMOVED'


# Słowniki:
OSW_ilDetRuchuLatarnia_1_LIST = ['latarnia bez detektora', '1 detektor', '2 detektory', '3 detektory', '4 detektory']
OSW_ilOprawLatarnia_2_LIST = ['1 oprawa', '2 oprawy', '3 oprawy', '4 oprawy']
OSW_ilWnek_3_LIST = ['1 wnęka', '2 wnęki']
OSW_kolorSlupa_4_LIST = ['RAL 7016', 'INOX', 'ocynkowany naturalny', 'anodowany naturalny', 'grafitowy', 'inny']
OSW_nachylenieWysiegnika_5_LIST = ['0 stopni', '5 stopni', '10 stopni', '15 stopni', '20 stopni']
OSW_producentOprawy_6_LIST = ['OCP - Parkowa', 'Philips SGS 101', 'Philips SGS 102', 'Philips SGS 103', 'Philips SGS 203', 'Philips SGS 305', 'Philips SGS 306', 'Rosa LUNOIDA', 'Schreder ALBANY', 'Schreder AMBAR', 'Schreder AMBAR 2', 'Schreder Ampera', 'Schreder FURYO', 'Schreder HAPILED', 'Schreder ISLA', 'Schreder OPALO 1', 'Schreder TECEO', 'Schreder YMERA', 'Schreder YOA']
OSW_producentSlupa_7_LIST = ['Rosa', 'Elektromontaż Rzeszów', 'Valmont', 'Kromiss-Bis', 'Elomnter', 'EuroPoles', 'Strunobet', 'Mabo']
OSW_punktyPodzialowe_8_LIST = ['złącze kablowe', 'złącze rozdzielcze', 'złącze podziałowe']
OSW_rodzajDet_9_LIST = ['mikrofalowy', 'PIR']
OSW_rodzajspsStatecznika_10_LIST = ['elektromagnetyczny', 'elektroniczny', 'LED analogowy 1-10V', 'LED cyfrowy DALI']
OSW_rodzajWysiegnika_11_LIST = ['1 ramienny', '2 ramienny (typ T)', '2 ramienny (typ V)', '3 ramienny', '4 ramienny']
OSW_typOprawy_12_LIST = ['LED', 'sodowa', 'metalohalogenkowa', 'rtęciowa', 'inna']
OSW_typSlupa_13_LIST = ['stalowy ocynkowany', 'stalowy malowany', 'aluminiowy malowany', 'aluminiowy anodowany', 'betonowy OZ naturalny', 'betonowy OZ malowany', 'betonowy WZ naturalny', 'betonowy WZ malowany', 'latarnia bez słupa']
OSW_typSterownikaLatarnia_14_LIST = ['z "R"', 'bez "R"', 'kompaktowy']


#====================================================================================================================


import os
import time
import random
import shutil
#import urllib.request
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from qgis.core import *
from qgis.utils import iface
from .Logger import Logger

LEFT_SPACING = '  '
CELL_1_WIDTH = 230
CELL_2_WIDTH = 540
CELL_HEIGHT = 30
CELL_SEP = 1
BUTTON_SEP_X = 1
BUTTON_SEP_Y = 1
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 28
LAYERS_NAME_LIST = ['latarnie', 'punkty_podzialu', 'szafy_oswietleniowe', 'zdzit_latarnia_detektor', 'zdzit_latarnia_oprawa', 'zdzit_latarnia_oprawa_attach', 'latarnia_attach', 'szafa_oswietleniowa_attach', 'punkt_podzialu_attach']
LAYERS_DICT = {}
MAX_GLOBALID_LEN = 38
EDITING_FIELDS_LIST = []
BUTTONS_LIST = []

FIELD_TO_DICT_MAP = {
        'ile_det_ruchu_w_latarni': OSW_ilDetRuchuLatarnia_1_LIST,
        'ile_opraw_w_latarni': OSW_ilOprawLatarnia_2_LIST,
        'ile_wnek': OSW_ilWnek_3_LIST,
        'kolor_slupa': OSW_kolorSlupa_4_LIST,
        'nachylenie_wysiegnika': OSW_nachylenieWysiegnika_5_LIST,
        'producent_oprawy': OSW_producentOprawy_6_LIST,
        'producent_slupa': OSW_producentSlupa_7_LIST,
        'rodzaj_zlacza': OSW_punktyPodzialowe_8_LIST,
        'rodzaj_det': OSW_rodzajDet_9_LIST,
        'rodzaj_sps_stat_w_opr': OSW_rodzajspsStatecznika_10_LIST,
        'rodzaj_wysiegnika': OSW_rodzajWysiegnika_11_LIST,
        'typ_oprawy': OSW_typOprawy_12_LIST,
        'typ_slupa': OSW_typSlupa_13_LIST,
        'typ_sterownika': OSW_typSterownikaLatarnia_14_LIST
    }
NOT_CHANGED_STYLE = "background-color:rgb(255,255,255)"
CHANGED_STYLE = "background-color:rgb(255,255,0)"
ALL_GLOBALID_LIST = []
GLOBALID_MAX_LEN = 38


class TO_data_editing(QtWidgets.QMainWindow):


    def __init__(self, iface):
        super(TO_data_editing, self).__init__()
        self.iface = iface
        self.base_path = os.sep.join(os.path.realpath(__file__).split(os.sep)[0:-1])
        self.icon = QtGui.QIcon(os.path.join(self.base_path, 'img', 'TO_data_editing_ICON.png'))
        self.logger = Logger(os.path.join(self.base_path, 'log', 'TO_data_editing.log'), 10 * 1024, 4, 'TO_data_editing')
        self.selected_feature = None
        self.r = 0
        self.any_edit_field_changed = False
        self.print_info('__init__ - OK.')


    def closeEvent(self, event):
        self._remove_widgets_from_gridLayout()
        event.accept()


    #----------------------------------------------------------------------------------------------------------------
    # plugin methods:
    

    def initGui(self):
        self.action = QtWidgets.QAction(self.icon, SCRIPT_TITLE, self.iface.mainWindow())
        self.action.setObjectName(SCRIPT_NAME + '_action')
        self.iface.addToolBarIcon(self.action)
        self.action.triggered.connect(self.run)
        uic.loadUi(os.path.join(self.base_path, 'ui', 'TO_data_editing.ui'), self)
        self.setWindowTitle(SCRIPT_TITLE + ' v. ' + SCRIPT_VERSION)
        self.About_pushButton.clicked.connect(self.about_pushButton_clicked)
        self.Man_pushButton.clicked.connect(self.man_pushButton_clicked)
        self.Zamknij_pushButton.clicked.connect(self.zamknij_pushButton_clicked)
        self.print_info('initGui - OK.')
        
        
    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.action.triggered.disconnect(self.run)
        self.About_pushButton.clicked.disconnect(self.about_pushButton_clicked)
        self.Man_pushButton.clicked.disconnect(self.man_pushButton_clicked)
        self.Zamknij_pushButton.clicked.disconnect(self.zamknij_pushButton_clicked)
        self.print_info('unload - OK.')


    def run(self):
        global LAYERS_DICT
        if not LAYERS_DICT:
            for layer_name in LAYERS_NAME_LIST:
                tmp_layer = self.get_layer(layer_name)
                if tmp_layer:
                    LAYERS_DICT[layer_name] = tmp_layer
                else:
                    return
        n = 0
        for tmp_layer in LAYERS_DICT.values():
            if tmp_layer == self.iface.activeLayer():
                n += 1
        if n == 0:
            QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, "Brak odpowiedniej wybranej warstwy.")
            return
        if n > 1:
            QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, "Jest więcej niż jedna wybrana warstwa.")
            return
        if self.iface.activeLayer().selectedFeatureCount() != 1:
            QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, "Trzeba wybrać jeden obiekt.")
            return
        self.selected_feature = self.iface.activeLayer().selectedFeatures()[0]

        if self.iface.activeLayer().name() == 'latarnie':
            self.gridLayout.addWidget(self._get_QLabel('latarnia:', CELL_1_WIDTH, CELL_HEIGHT), self.r, 0)
            layout = QtWidgets.QHBoxLayout()
            self.add_button(layout, 'dodaj załącznik', self.dodaj_zalacznik, self.selected_feature['globalid'], LAYERS_DICT['latarnia_attach'])
            self.add_button(layout, 'dodaj detektor', self.dodaj_detektor, self.selected_feature['globalid'], None)
            self.add_button(layout, 'dodaj oprawę', self.dodaj_oprawe, self.selected_feature['globalid'], None)
            self.add_button(layout, 'usuń obiekt', self.usun_obiekt, self.selected_feature, LAYERS_DICT['latarnie'])
            self.gridLayout.addLayout(layout, self.r, 1)
            self.r += 1
            for field in LAYERS_DICT['latarnie'].fields():
                self.add_row(LAYERS_DICT['latarnie'], self.selected_feature, field.name())
            self.add_blank_row()
            current_globalid = str(self.selected_feature.attribute('globalid'))
            for fet in LAYERS_DICT['latarnia_attach'].getFeatures():
                if fet.attribute('rel_globalid') == current_globalid:
                    layout = QtWidgets.QHBoxLayout()
                    self.gridLayout.addWidget(self._get_QLabel(fet.attribute('file_name'), CELL_1_WIDTH, CELL_HEIGHT), self.r, 0)
                    self.add_button(layout, 'pokaż obiekt', self.pokaz_obiekt, fet.attribute('file_name'), None)
                    self.add_button(layout, 'usuń obiekt', self.usun_obiekt, fet, LAYERS_DICT['latarnia_attach'])
                    self.gridLayout.addLayout(layout, self.r, 1)
                    self.r += 1
            for fet in LAYERS_DICT['zdzit_latarnia_detektor'].getFeatures():
                if fet.attribute('latarnia_id') == current_globalid:
                    self.add_blank_row()
                    self.add_blank_row()
                    layout = QtWidgets.QHBoxLayout()
                    self.gridLayout.addWidget(self._get_QLabel('detektor:', CELL_1_WIDTH, CELL_HEIGHT), self.r, 0)
                    self.add_button(layout, 'usuń obiekt', self.usun_obiekt, fet, LAYERS_DICT['zdzit_latarnia_detektor'])
                    self.gridLayout.addLayout(layout, self.r, 1)
                    self.r += 1
                    for field in LAYERS_DICT['zdzit_latarnia_detektor'].fields():
                        self.add_row(LAYERS_DICT['zdzit_latarnia_detektor'], fet, field.name())
            for fet in LAYERS_DICT['zdzit_latarnia_oprawa'].getFeatures():
                if fet.attribute('latarnia_id') == current_globalid:
                    self.add_blank_row()
                    self.add_blank_row()
                    layout = QtWidgets.QHBoxLayout()
                    self.gridLayout.addWidget(self._get_QLabel('oprawa:', CELL_1_WIDTH, CELL_HEIGHT), self.r, 0)
                    self.add_button(layout, 'dodaj załącznik', self.dodaj_zalacznik, fet.attribute('globalid'), LAYERS_DICT['zdzit_latarnia_oprawa_attach'])
                    self.add_button(layout, 'usuń obiekt', self.usun_obiekt, fet, LAYERS_DICT['zdzit_latarnia_oprawa'])
                    self.gridLayout.addLayout(layout, self.r, 1)
                    self.r += 1
                    for field in LAYERS_DICT['zdzit_latarnia_oprawa'].fields():
                        self.add_row(LAYERS_DICT['zdzit_latarnia_oprawa'], fet, field.name())
                    self.add_blank_row()
                    oprawa_globalid = fet.attribute('globalid')
                    tmp_r = self.r
                    for fet_2 in LAYERS_DICT['zdzit_latarnia_oprawa_attach'].getFeatures():
                        if fet_2.attribute('rel_globalid') == oprawa_globalid:
                            layout = QtWidgets.QHBoxLayout()
                            self.gridLayout.addWidget(self._get_QLabel(fet_2.attribute('file_name'), CELL_1_WIDTH, CELL_HEIGHT), self.r, 0)
                            self.add_button(layout, 'pokaż obiekt', self.pokaz_obiekt, fet_2.attribute('file_name'), None)
                            self.add_button(layout, 'usuń obiekt', self.usun_obiekt, fet_2, LAYERS_DICT['zdzit_latarnia_oprawa_attach'])
                            self.gridLayout.addLayout(layout, self.r, 1)
                            self.r += 1
                    if tmp_r < self.r:
                        self.add_blank_row()
                        self.add_blank_row()
        elif self.iface.activeLayer().name() == 'punkty_podzialu':
            layout = QtWidgets.QHBoxLayout()
            self.gridLayout.addWidget(self._get_QLabel('punkt podziału:', CELL_1_WIDTH, CELL_HEIGHT), self.r, 0)
            self.add_button(layout, 'dodaj załącznik', self.dodaj_zalacznik, self.selected_feature['globalid'], LAYERS_DICT['punkt_podzialu_attach'])
            self.add_button(layout, 'usuń obiekt', self.usun_obiekt, self.selected_feature, LAYERS_DICT['punkty_podzialu'])
            self.gridLayout.addLayout(layout, self.r, 1)
            self.r += 1
            for field in LAYERS_DICT['punkty_podzialu'].fields():
                self.add_row(LAYERS_DICT['punkty_podzialu'], self.selected_feature, field.name())
            self.add_blank_row()
            self.add_blank_row()
            current_globalid = str(self.selected_feature.attribute('globalid'))
            for fet in LAYERS_DICT['punkt_podzialu_attach'].getFeatures():
                if fet.attribute('rel_globalid') == current_globalid:
                    layout = QtWidgets.QHBoxLayout()
                    self.gridLayout.addWidget(self._get_QLabel(fet.attribute('file_name'), CELL_1_WIDTH, CELL_HEIGHT), self.r, 0)
                    self.add_button(layout, 'pokaż obiekt', self.pokaz_obiekt, fet.attribute('file_name'), None)
                    self.add_button(layout, 'usuń obiekt', self.usun_obiekt, fet, LAYERS_DICT['punkt_podzialu_attach'])
                    self.gridLayout.addLayout(layout, self.r, 1)
                    self.r += 1
        elif self.iface.activeLayer().name() == 'szafy_oswietleniowe':
            layout = QtWidgets.QHBoxLayout()
            self.gridLayout.addWidget(self._get_QLabel('szafa oświetleniowa:', CELL_1_WIDTH, CELL_HEIGHT), self.r, 0)
            self.add_button(layout, 'dodaj załącznik', self.dodaj_zalacznik, self.selected_feature['globalid'], LAYERS_DICT['szafa_oswietleniowa_attach'])
            self.add_button(layout, 'usuń obiekt', self.usun_obiekt, self.selected_feature, LAYERS_DICT['szafy_oswietleniowe'])
            self.gridLayout.addLayout(layout, self.r, 1)
            self.r += 1
            for field in LAYERS_DICT['szafy_oswietleniowe'].fields():
                self.add_row(LAYERS_DICT['szafy_oswietleniowe'], self.selected_feature, field.name())
            self.add_blank_row()
            self.add_blank_row()
            current_globalid = str(self.selected_feature.attribute('globalid'))
            for fet in LAYERS_DICT['szafa_oswietleniowa_attach'].getFeatures():
                if fet.attribute('rel_globalid') == current_globalid:
                    layout = QtWidgets.QHBoxLayout()
                    self.gridLayout.addWidget(self._get_QLabel(fet.attribute('file_name'), CELL_1_WIDTH, CELL_HEIGHT), self.r, 0)
                    self.add_button(layout, 'pokaż obiekt', self.pokaz_obiekt, fet.attribute('file_name'), None)
                    self.add_button(layout, 'usuń obiekt', self.usun_obiekt, fet, LAYERS_DICT['szafa_oswietleniowa_attach'])
                    self.gridLayout.addLayout(layout, self.r, 1)
                    self.r += 1
        else:
            QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, "Brak odpowiedniej wybranej warstwy (tylko: latarnie, punkty_podzialu lub szafy_oswietleniowe).")
        _new_rect = QtCore.QRect(0, 0, CELL_1_WIDTH + CELL_2_WIDTH, self.r * (CELL_HEIGHT + 2 * CELL_SEP))
        self.scrollAreaWidgetContents.setGeometry(_new_rect)
        self.gridLayoutWidget.setGeometry(_new_rect)
        self.gridLayoutWidget.setStyleSheet("background-color:rgb(0,0,0)")
        self.show()
        

    #----------------------------------------------------------------------------------------------------------------
    # input widget methods


    def man_pushButton_clicked(self):
        if MANUAL_FILE_NAME and len(MANUAL_FILE_NAME) > 0 and MANUAL_FILE_NAME.upper().endswith('.PDF'):
            try:
                os.startfile(os.path.join(self.base_path, 'doc', MANUAL_FILE_NAME))
            except:
                QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, 'Nie można otworzyć instrukcji.')


    def zamknij_pushButton_clicked(self):
        if self.any_edit_field_changed:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Question)
            msgBox.setText('Zapisać zmiany?')
            msgBox.setWindowTitle(SCRIPT_TITLE)
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            res = msgBox.exec()
            if res == QtWidgets.QMessageBox.Yes:
                for editing_field_dict in EDITING_FIELDS_LIST:
                    try:
                        oryginal_att_text = ''
                        if str(editing_field_dict['feature'][editing_field_dict['field_name']]) != 'NULL':
                            oryginal_att_text = str(editing_field_dict['feature'][editing_field_dict['field_name']])
                        if oryginal_att_text != self.get_text_from_edit_field(editing_field_dict):
                            with edit(editing_field_dict['layer']):
                                editing_field_dict['feature'][editing_field_dict['field_name']] = self.get_text_from_edit_field(editing_field_dict)
                                editing_field_dict['layer'].updateFeature(editing_field_dict['feature'])
                    except:
                        problem_data_str = self.get_text_from_edit_field(editing_field_dict)
                        editing_field_dict['layer'].rollBack()
                        self.set_text_to_edit_field(editing_field_dict, oryginal_att_text)
                        QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, 'ERROR: ' + editing_field_dict['field_name'] + ' = ' + problem_data_str)
                        break
            elif res == QtWidgets.QMessageBox.Cancel:
                return
        else:
            QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, 'Nie było zmian danych.')
        self._remove_widgets_from_gridLayout()
        self.hide()


    def about_pushButton_clicked(self):
        QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, SCRIPT_TITLE + ' v. ' + SCRIPT_VERSION + '\n' + GENERAL_INFO)


    def edit_field_textChanged(self, new_tx = None):
        self.any_edit_field_changed = False
        for editing_field_dict in EDITING_FIELDS_LIST:
            oryginal_att_text = ''
            if str(editing_field_dict['feature'][editing_field_dict['field_name']]) != 'NULL':
                oryginal_att_text = str(editing_field_dict['feature'][editing_field_dict['field_name']])
            if oryginal_att_text != self.get_text_from_edit_field(editing_field_dict):
                self.any_edit_field_changed = True
                editing_field_dict['edit_field'].setStyleSheet(CHANGED_STYLE)
            else:
                editing_field_dict['edit_field'].setStyleSheet(NOT_CHANGED_STYLE)            


    #----------------------------------------------------------------------------------------------------------------
    # aux methods:


    def add_row(self, layer, feature, field_name):
        self.gridLayout.addWidget(self._get_QLabel(field_name, CELL_1_WIDTH, CELL_HEIGHT), self.r, 0)
        if field_name == 'id' or field_name == 'globalid' or field_name == 'rel_globalid' or field_name == 'latarnia_id':
            self.gridLayout.addWidget(self._get_QLabel(feature[field_name], CELL_2_WIDTH, CELL_HEIGHT), self.r, 1)
        elif field_name in FIELD_TO_DICT_MAP.keys():
            self.gridLayout.addWidget(self._get_QComboBox(layer, feature, field_name, CELL_2_WIDTH, CELL_HEIGHT, FIELD_TO_DICT_MAP[field_name]), self.r, 1)
        else:
            self.gridLayout.addWidget(self._get_QLineEdit(layer, feature, field_name, CELL_2_WIDTH, CELL_HEIGHT), self.r, 1)
        self.r += 1


    def add_blank_row(self):
        self.gridLayout.addWidget(self._get_QLabel('', CELL_1_WIDTH, CELL_HEIGHT), self.r, 0)
        self.gridLayout.addWidget(self._get_QLabel('', CELL_2_WIDTH, CELL_HEIGHT), self.r, 1)
        self.r += 1


    def dodaj_zalacznik(self, parent_globalid, layer_to_add_to):
        new_globalid = self.get_globalid_str(GLOBALID_MAX_LEN)
        if new_globalid:
            new_fields = QgsFields()
            new_fields.append(QgsField('globalid', QtCore.QVariant.String))
            new_fields.append(QgsField('rel_globalid', QtCore.QVariant.String))
            new_fields.append(QgsField('file_name', QtCore.QVariant.String))
            new_feature = QgsFeature()
            new_feature.setFields(new_fields)
            new_feature.setAttribute('globalid', new_globalid)
            new_feature.setAttribute('rel_globalid', parent_globalid)
            path_to_file = QtWidgets.QFileDialog.getOpenFileName(self, 'dodaj załącznik (tabela: ' + layer_to_add_to.name() + ')')[0]
            if path_to_file and len(path_to_file) >= 1:
                file_name = os.path.basename(path_to_file)
                file_name = self.get_unique_file_name(file_name, PATH_TO_ATTACHMENTS_FOLDER)
                shutil.copy2(path_to_file, os.path.join(PATH_TO_ATTACHMENTS_FOLDER, file_name))
                new_feature.setAttribute('file_name', file_name)
                with edit(layer_to_add_to):
                    layer_to_add_to.addFeature(new_feature)
                self._remove_widgets_from_gridLayout()
                self.run()
                QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, 'Dodano załącznik.')
            else:
                QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, 'dodaj_zalacznik PROBLEM(path_to_file)')
        else:
            QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, 'dodaj_zalacznik PROBLEM(new_globalid)')


    def usun_obiekt(self, feature_to_remove, layer_to_remove_from, verbose = True):
        global LAYERS_DICT
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        msgBox.setText('Usunąć obiekt?')
        msgBox.setWindowTitle(SCRIPT_TITLE)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        res = msgBox.exec()
        if res == QtWidgets.QMessageBox.Yes:
            if layer_to_remove_from.name() == 'latarnie':
                current_globalid = feature_to_remove.attribute('globalid')
                with edit(layer_to_remove_from):
                    layer_to_remove_from.deleteFeature(feature_to_remove.id())
                for fet_2 in LAYERS_DICT['latarnia_attach'].getFeatures():
                    if fet_2.attribute('rel_globalid') == current_globalid:
                        self.usun_obiekt(fet_2, LAYERS_DICT['latarnia_attach'], False)
                for fet_2 in LAYERS_DICT['zdzit_latarnia_detektor'].getFeatures():
                    if fet_2.attribute('latarnia_id') == current_globalid:
                        self.usun_obiekt(fet_2, LAYERS_DICT['zdzit_latarnia_detektor'], False)
                for fet_2 in LAYERS_DICT['zdzit_latarnia_oprawa'].getFeatures():
                    if fet_2.attribute('latarnia_id') == current_globalid:
                        self.usun_obiekt(fet_2, LAYERS_DICT['zdzit_latarnia_oprawa'], False)
                self._remove_widgets_from_gridLayout()
                self.hide()
                QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, 'Usunięto latarnię z zależnościami.')
            elif layer_to_remove_from.name() == 'punkty_podzialu':
                current_globalid = feature_to_remove.attribute('globalid')
                with edit(layer_to_remove_from):
                    layer_to_remove_from.deleteFeature(feature_to_remove.id())
                for fet_2 in LAYERS_DICT['punkt_podzialu_attach'].getFeatures():
                    if fet_2.attribute('rel_globalid') == current_globalid:
                        self.usun_obiekt(fet_2, LAYERS_DICT['punkt_podzialu_attach'], False)
                self._remove_widgets_from_gridLayout()
                self.hide()
                QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, 'Usunięto punkt podziału z załącznikami.')
            elif layer_to_remove_from.name() == 'szafy_oswietleniowe':
                current_globalid = feature_to_remove.attribute('globalid')
                with edit(layer_to_remove_from):
                    layer_to_remove_from.deleteFeature(feature_to_remove.id())
                for fet_2 in LAYERS_DICT['szafa_oswietleniowa_attach'].getFeatures():
                    if fet_2.attribute('rel_globalid') == current_globalid:
                        self.usun_obiekt(fet_2, LAYERS_DICT['szafa_oswietleniowa_attach'], False)
                self._remove_widgets_from_gridLayout()
                self.hide()
                QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, 'Usunięto szafę oświetleniową z załącznikami.')
            elif layer_to_remove_from.name() == 'zdzit_latarnia_detektor':
                with edit(layer_to_remove_from):
                    layer_to_remove_from.deleteFeature(feature_to_remove.id())
                if verbose:
                    self._remove_widgets_from_gridLayout()
                    self.run()
                    QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, 'Usunięto detektor.')
            elif layer_to_remove_from.name() == 'zdzit_latarnia_oprawa':
                oprawa_globalid = feature_to_remove.attribute('globalid')
                with edit(layer_to_remove_from):
                    layer_to_remove_from.deleteFeature(feature_to_remove.id())
                for fet_2 in LAYERS_DICT['zdzit_latarnia_oprawa_attach'].getFeatures():
                    if fet_2.attribute('rel_globalid') == oprawa_globalid:
                        self.usun_obiekt(fet_2, LAYERS_DICT['zdzit_latarnia_oprawa_attach'], False)
                if verbose:
                    self._remove_widgets_from_gridLayout()
                    self.run()
                    QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, 'Usunięto oprawę z załącznikami.')
            elif layer_to_remove_from.name().endswith('_attach'):
                file_name = feature_to_remove.attribute('file_name')
                if os.path.exists(os.path.join(PATH_TO_ATTACHMENTS_FOLDER, file_name)):
                    file_name_2 = self.get_unique_file_name(file_name, PATH_TO_REMOVED_ATTACHMENTS_FOLDER)
                    shutil.move(os.path.join(PATH_TO_ATTACHMENTS_FOLDER, file_name), os.path.join(PATH_TO_REMOVED_ATTACHMENTS_FOLDER, file_name_2))
                elif verbose:
                    QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, 'Brak pliku załącznika: ' + str(file_name))
                with edit(layer_to_remove_from):
                    layer_to_remove_from.deleteFeature(feature_to_remove.id())
                if verbose:
                    self._remove_widgets_from_gridLayout()
                    self.run()
                    QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, 'Usunięto załącznik (plik przeniesiono do folderu usuniętych załączników).')
            else:
                QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, 'usun_obiekt PROBLEM: błędna nazwa warstwy: ' + str(layer_to_remove_from.name()))
        

    def pokaz_obiekt(self, file_name, arg_2 = None):
        if file_name and len(file_name) > 0:
            try:
                os.startfile(os.path.join(PATH_TO_ATTACHMENTS_FOLDER, file_name))
            except:
                QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, 'Nie można otworzyć załącznika.')


    def dodaj_oprawe(self, latarnia_id, arg_2 = None):
        global LAYERS_DICT
        new_globalid = self.get_globalid_str(GLOBALID_MAX_LEN)
        if new_globalid:
            new_fields = QgsFields()
            new_fields.append(QgsField('globalid', QtCore.QVariant.String))
            new_fields.append(QgsField('latarnia_id', QtCore.QVariant.String))
            new_fields.append(QgsField('nachylenie_wysiegnika', QtCore.QVariant.Int))
            new_fields.append(QgsField('moc_oprawy_znamion', QtCore.QVariant.Double))
            new_fields.append(QgsField('wys_zaw_oprawy', QtCore.QVariant.Double))
            new_fields.append(QgsField('moc_oprawy_obciaz', QtCore.QVariant.Double))
            new_fields.append(QgsField('rodzaj_wysiegnika', QtCore.QVariant.String))
            new_fields.append(QgsField('typ_oprawy', QtCore.QVariant.String))
            new_fields.append(QgsField('producent_oprawy', QtCore.QVariant.String))
            new_fields.append(QgsField('rodzaj_sps_stat_w_opr', QtCore.QVariant.String))
            new_fields.append(QgsField('wysieg_wysiegnika', QtCore.QVariant.Double))
            new_fields.append(QgsField('sps_ster_oprawy', QtCore.QVariant.String))
            new_fields.append(QgsField('montaz_oprawy', QtCore.QVariant.Double))
            new_fields.append(QgsField('stan_wysiegnika', QtCore.QVariant.String))
            new_fields.append(QgsField('stan_oprawy', QtCore.QVariant.String))
            new_fields.append(QgsField('uwagi', QtCore.QVariant.String))
            new_feature = QgsFeature()
            new_feature.setFields(new_fields)
            new_feature.setAttribute('globalid', new_globalid)
            new_feature.setAttribute('latarnia_id', latarnia_id)
            with edit(LAYERS_DICT['zdzit_latarnia_oprawa']):
                LAYERS_DICT['zdzit_latarnia_oprawa'].addFeature(new_feature) 
            self._remove_widgets_from_gridLayout()
            self.run()
            QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, 'Dodano oprawę.')
        else:
            QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, 'dodaj_oprawe PROBLEM(new_globalid)')


    def dodaj_detektor(self, latarnia_id, arg_2 = None):
        global LAYERS_DICT
        new_globalid = self.get_globalid_str(GLOBALID_MAX_LEN)
        if new_globalid:
            new_fields = QgsFields()
            new_fields.append(QgsField('globalid', QtCore.QVariant.String))
            new_fields.append(QgsField('latarnia_id', QtCore.QVariant.String))
            new_fields.append(QgsField('rodzaj_det', QtCore.QVariant.String))
            new_feature = QgsFeature()
            new_feature.setFields(new_fields)
            new_feature.setAttribute('globalid', new_globalid)
            new_feature.setAttribute('latarnia_id', latarnia_id)
            with edit(LAYERS_DICT['zdzit_latarnia_detektor']):
                LAYERS_DICT['zdzit_latarnia_detektor'].addFeature(new_feature)
            self._remove_widgets_from_gridLayout()
            self.run()
            QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, 'Dodano detektor.')
        else:
            QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, 'dodaj_detektor PROBLEM(new_globalid)')


    def add_button(self, layout, title, func, arg_1, arg_2 = None):
        global BUTTONS_LIST
        button = QtWidgets.QPushButton(title, self)
        button.setGeometry(BUTTON_SEP_X, BUTTON_SEP_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        button.clicked.connect(lambda _: func(arg_1, arg_2))
        button.setStyleSheet("background-color:rgb(230,230,230)")
        layout.addWidget(button)
        BUTTONS_LIST.append(button)


    def _get_QLabel(self, tx, width, height):
        _tmp_label = QtWidgets.QLabel(self)
        _tmp_label.setGeometry(QtCore.QRect(CELL_SEP, CELL_SEP, width, height))
        _tmp_label.setMinimumSize(width, height)
        _tmp_label.setMaximumSize(width, height)
        _tmp_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        _tmp_label.setStyleSheet("background-color:rgb(200,200,200)")
        _tmp_label.setText(LEFT_SPACING + str(tx))
        return _tmp_label


    def _get_QLineEdit(self, layer, feature, field_name, width, height):
        global EDITING_FIELDS_LIST
        _tmp_LineEdit = QtWidgets.QLineEdit(self)
        _tmp_LineEdit.setGeometry(QtCore.QRect(CELL_SEP, CELL_SEP, width, height))
        _tmp_LineEdit.setMinimumSize(width, height)
        _tmp_LineEdit.setMaximumSize(width, height)
        _tmp_LineEdit.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        _tmp_LineEdit.setStyleSheet(NOT_CHANGED_STYLE)
        editing_field_dict = {'layer':layer, 'feature':feature, 'field_name':field_name, 'edit_field':_tmp_LineEdit, 'edit_field_type': 'LineEdit'}
        EDITING_FIELDS_LIST.append(editing_field_dict)
        self.set_text_to_edit_field(editing_field_dict, str(feature[field_name]))
        _tmp_LineEdit.textChanged.connect(self.edit_field_textChanged)
        return _tmp_LineEdit


    def _get_QComboBox(self, layer, feature, field_name, width, height, dict_list):
        global EDITING_FIELDS_LIST
        _tmp_ComboBox = QtWidgets.QComboBox(self)
        _tmp_ComboBox.setGeometry(QtCore.QRect(CELL_SEP, CELL_SEP, width, height))
        _tmp_ComboBox.setMinimumSize(width, height)
        _tmp_ComboBox.setMaximumSize(width, height)
        _tmp_ComboBox.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        _tmp_ComboBox.setStyleSheet(NOT_CHANGED_STYLE)
        _tmp_ComboBox.addItems(dict_list)
        _tmp_ComboBox.setEditable(True)
        editing_field_dict = {'layer':layer, 'feature':feature, 'field_name':field_name, 'edit_field':_tmp_ComboBox, 'edit_field_type': 'ComboBox'}
        EDITING_FIELDS_LIST.append(editing_field_dict)
        self.set_text_to_edit_field(editing_field_dict, str(feature[field_name]))
        _tmp_ComboBox.currentTextChanged.connect(self.edit_field_textChanged)
        return _tmp_ComboBox


    def set_text_to_edit_field(self, editing_field_dict, text):
        if not text or text == 'NULL':
            text = ''
        if editing_field_dict['edit_field_type'] == 'LineEdit':
            editing_field_dict['edit_field'].setText(text)
        else:
            if not text in FIELD_TO_DICT_MAP[editing_field_dict['field_name']]:
                editing_field_dict['edit_field'].addItem(text)
            idx = editing_field_dict['edit_field'].findText(text)
            editing_field_dict['edit_field'].setCurrentIndex(idx)


    def get_text_from_edit_field(self, editing_field_dict):
        if editing_field_dict['edit_field_type'] == 'LineEdit':
            return str(editing_field_dict['edit_field'].text())
        else:
            return str(editing_field_dict['edit_field'].currentText())


    def get_layer(self, layer_name):
        try:
            return QgsProject.instance().mapLayersByName(layer_name)[0]
        except:
            QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, "There is no '" + str(layer_name) + "' layer.")
            return None


    def _remove_widgets_from_gridLayout(self):
        global EDITING_FIELDS_LIST
        global BUTTONS_LIST
        for button in BUTTONS_LIST:
            try:
                button.setParent(None)
                del button
            except:
                pass
        for i in reversed(range(self.gridLayout.count())):
            try:
                widget_to_remove = self.gridLayout.itemAt(i).widget()
                self.gridLayout.removeWidget(widget_to_remove)
                widget_to_remove.setParent(None)
                del widget_to_remove
            except:
                pass
        self.r = 0
        EDITING_FIELDS_LIST = []
        BUTTONS_LIST = []
        self.any_edit_field_changed = False


    def get_unique_file_name(self, file_name, folder):
        if not os.path.exists(os.path.join(folder, file_name)):
            return file_name
        file_name_list = os.path.splitext(file_name)
        if len(file_name_list) == 2:
            base_file_name = file_name_list[0]
            extension_of_file_name = file_name_list[1]
            random.seed()
            s = str(int(random.random() * 1000))
            b = int(random.random() * 1000000)
            i = 0
            while True:
                if os.path.exists(os.path.join(folder, base_file_name + '(' + s + '_' + str(b + i) + ')' + extension_of_file_name)):
                    i += 1
                    if i > 10:
                        break
                else:
                    return base_file_name + '(' + s + '_' + str(b + i) + ')' + extension_of_file_name
        return None


    def get_globalid_str(self, mx_len):
        if not ALL_GLOBALID_LIST:
            for layer in LAYERS_DICT.values():
                for feature in layer.getFeatures():
                    ALL_GLOBALID_LIST.append(feature['globalid'])
        random.seed()
        i = 0
        while True:
            global_id_str = hex(int(time.time() * 1000000)) + '-' + hex(int(random.random() * 10000000000000000)) + '-' + hex(int(random.random() * 10000000000000000))
            global_id_str = global_id_str.replace('0x', '')
            if len(global_id_str) > mx_len - 2:
                global_id_str = global_id_str[0:mx_len-2]
            global_id_str = '{' + global_id_str.upper() + '}'
            if not global_id_str in ALL_GLOBALID_LIST:
                ALL_GLOBALID_LIST.append(global_id_str)
                break
            if i > 10:
                return None
            else:
                i += 1
        return global_id_str


    def print_info(self, info):
        if self.logger and LOGGER:
            self.logger.write_INFO_log(info)
        else:
            print(info)


#====================================================================================================================
    
