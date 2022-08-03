import os, math, sys, mysql.connector, configparser, locale, time, tempfile, traceback
from datetime import datetime, date
from PyQt5.QtCore import Qt, QRegExp, QEvent, QDate, QUrl, QFile, QTextStream, QThread, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QFont, QRegExpValidator, QDesktopServices, QColor
from PyQt5.QtWidgets import QSplashScreen, QLineEdit, QStatusBar, QAbstractSpinBox, QHeaderView, QTableWidgetItem, QMainWindow, QMdiSubWindow, QWidget, QApplication, QFileDialog, QComboBox, QMessageBox,QProgressBar
from PyQt5.uic import loadUi
from filelock import FileLock, Timeout

""" Clase que administra el conector para la base de datos """
class DbLocal:
	""" Clase que instancia el conector a la base de datos, los datos se conexión
		se guardan en un .ini en la carpeta raiz """
	
	def __init__(self):
		self.cnx = mysql.connector.connect(
			user = config['DEFAULT']['DB_USER'],
			password = config['DEFAULT']['DB_PASSWORD'],
			host = config['DEFAULT']['DB_HOST'],
			port = config['DEFAULT']['DB_PORT'],
			database = config['DEFAULT']['DB_NAME'],
			autocommit = True,
			buffered=True)
		self.cursor = self.cnx.cursor()

	##==============================================##
	def Close(self):
		self.cnx.close()

	##==============================================##
	def Queryone(self, arg):
		self.cursor.execute(arg)
		row = self.cursor.fetchone()
		return row

	##==============================================##
	def Queryall(self, arg):
		self.cursor.execute(arg)
		rows = self.cursor.fetchall()
		return rows

	##==============================================##
	def Querymulti(self, arg):
		for result in self.cursor.execute(arg, multi=True):
			pass

""" Ventana principal la dejé tal cual el programa oficial, falntan muchas funciones."""
class VentanaPrincipal(QMainWindow):
	""" Clase principal, contenedora de todas las demás clases"""
	
	def __init__(self):
		super(VentanaPrincipal, self).__init__()
		loadUi('VentanaPrincipal.ui', self)
		locale.setlocale(locale.LC_ALL, '')
		self.setContextMenuPolicy(Qt.NoContextMenu)
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.Ini_SubWindows()
		self.installEventFilter(self)	
	
	# Gestor de eventos de la clase
	##==============================================##
	def eventFilter(self, target, event):
		''' Si el evento es de tipo teclado y es F12, se activa el boton de Contraseñas
		es una seguridad minima y facil de recordar que pidió el cliente '''
		if event.type() == QEvent.KeyPress and event.key() == Qt.Key_F12:
			self.Pass.setEnabled(not self.Pass.isEnabled())
		return False

	##==============================================##
	def CrearItem(self, item, tam, op):
		""" Funcion que setea y devuelve un item de tabla,
			segun lo los valores de entrada """
		aux = QTableWidgetItem(item)
		font = QFont()
		font.setPointSize(tam)
		font.setKerning(True)
		aux.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
		aux.setFont(font)
		if op == 'RS':
			aux.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
		elif op == 'R':
			aux.setFlags(Qt.ItemIsEnabled)
		elif op == 'T':
			aux.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
		aux.setTextAlignment(Qt.AlignCenter)
		return aux

	##==============================================##
	def Ini_SubWindows(self):
		""" Inicializacion de banderas que 
			previenen abrir 2 subwindows iguales """
		self.ListOpen = self.BDAOpen = False
		self.RankOpen = self.PrecOpen = False
		self.TabOpen = self.ZonOpen = False
		self.ProvOpen = self.ClienOpen = False
		self.CuenOpen = self.ProdOpen = False
		self.GastOpen = self.ComprOpen = False
		self.VentOpen = self.ResOpen = self.SetOpen = False
		self.EmOpen = self.FabTab = self.PassTab = False

	##==============================================##
	def CrearLogs(self):
		""" Crea o agrega a un logs.txt (en carpeta raíz) la informacion del error """
		f = open("logs.txt", "a")
		f.write(datetime.now().strftime("%d/%m/%Y") + ':' + '\n')
		for i in sys.exc_info():
			f.write(str(i) + '\n')
		f.write('\n')
		f.write(traceback.format_exc())
		f.write('------------' + '\n')
		f.close()

	##==============================================##
	def showAlerta(self, tipo = 1, Msg1 = '', Msg2 = ''):
		""" Despliega alertas de usuario"""
		msg = QMessageBox()
		if tipo == 1:
			msg.setWindowTitle("Advertencia")
			msg.setIcon(QMessageBox.Warning)
		else:
			msg.setWindowTitle("Informacion")
			msg.setIcon(QMessageBox.Information)
		msg.setText(Msg1)
		msg.setInformativeText(Msg2)	
		msg.setStandardButtons(QMessageBox.Ok)
		msg.setDefaultButton(QMessageBox.Ok)
		msg.exec()

	##==============================================##
	def AbrirMDI(self, opcion):
		""" Rutina que abre y centra los MDI que se abren """
		sub = QMdiSubWindow()
		sub.setWidget(opcion)
		sub.resize(sub.sizeHint())
		sub.setWindowFlags(Qt.WindowSystemMenuHint)
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.MDI.addSubWindow(sub)
		sub.show()
		center = self.MDI.viewport().rect().center()
		geo = sub.geometry()
		geo.moveCenter(center)
		sub.setGeometry(geo)
		sub.setFixedSize(sub.size())
		return sub

	##==============================================##
	""" Triggers de los botones, se instancian (las clases) a medida que se usa,
		y se destruyen a medida que se cierran. """

	def showPass(self):
		if not self.PassTab:
			self.PassTab = self.AbrirMDI(G_Pass())
		else:
			self.MDI.setActiveSubWindow(self.PassTab)

	def showFabTab(self):
		if not self.FabTab:
			self.FabTab = self.AbrirMDI(Fabrica_Tablas())
		else:
			self.MDI.setActiveSubWindow(self.FabTab)

	def showGastos(self):
		if not self.GastOpen:
			sub = Gastos()
			sub.setAttribute(Qt.WA_DeleteOnClose)
			sub.setWindowFlags(Qt.WindowCloseButtonHint)
			sub.show()
			self.GastOpen = sub

	def showEmail(self):
		if not self.EmOpen:
			self.EmOpen = self.AbrirMDI(Email())
		else:
			self.MDI.setActiveSubWindow(self.EmOpen)

	def showResC(self):
		if not self.ResOpen:
			self.MDI.closeAllSubWindows()
			self.ResOpen = self.AbrirMDI(Resumen_C())
		else:
			self.MDI.setActiveSubWindow(self.ResOpen)

	def showBDA(self):	
		if not self.BDAOpen:
			self.BDAOpen = self.AbrirMDI(Configuracion())
		else:
			self.MDI.setActiveSubWindow(self.BDAOpen)

	def showRankings(self):
		if not self.RankOpen:
			self.RankOpen = self.AbrirMDI(Rankings())
		else:
			self.MDI.setActiveSubWindow(self.RankOpen)

	def showListas(self):
		if not self.ListOpen:
			self.ListOpen = self.AbrirMDI(SelectList())
		else:
			self.MDI.setActiveSubWindow(self.ListOpen)

	def showPrecios(self):
		if not self.PrecOpen:
			self.PrecOpen = self.AbrirMDI(Precios())
		else:
			self.MDI.setActiveSubWindow(self.PrecOpen)

	def showCompras(self):
		if not self.ComprOpen:
			sub = Compras()
			sub.setAttribute(Qt.WA_DeleteOnClose)
			sub.setWindowFlags(Qt.WindowCloseButtonHint)
			sub.show()
			self.ComprOpen = sub

	def showTablas(self):
		if not self.TabOpen:
			self.TabOpen = self.AbrirMDI(Tablas())
		else:
			self.MDI.setActiveSubWindow(self.TabOpen)

	def showClientes(self):
		if not self.ClienOpen:
			self.ClienOpen = self.AbrirMDI(Clientes())
		else:
			self.MDI.setActiveSubWindow(self.ClienOpen)

	def showZonas(self):
		if not self.ZonOpen:
			self.ZonOpen = self.AbrirMDI(Zonas())
		else:
			self.MDI.setActiveSubWindow(self.ZonOpen)

	def showProve(self):
		if not self.ProvOpen:
			self.ProvOpen = self.AbrirMDI(Proveedores())
		else:
			self.MDI.setActiveSubWindow(self.ProvOpen)

	def showCuentas(self):
		if not self.CuenOpen:
			self.CuenOpen = self.AbrirMDI(Cuentas())
		else:
			self.MDI.setActiveSubWindow(self.CuenOpen)

	def showProductos(self):
		if not self.ProdOpen:
			self.ProdOpen = self.AbrirMDI(SelectProd())
		else:
			self.MDI.setActiveSubWindow(self.ProdOpen)

	def showVentas(self):
		if not self.VentOpen:
			sub = Ventas()
			sub.setAttribute(Qt.WA_DeleteOnClose)
			sub.setWindowFlags(Qt.WindowCloseButtonHint)
			sub.show()
			self.VentOpen = sub

	def showSeteo(self):
		if not self.SetOpen:
			self.SetOpen = self.AbrirMDI(Seteos())
		else:
			self.MDI.setActiveSubWindow(self.SetOpen)

	def showSalir(self):
		self.close()

	##==============================================##
	def Cerrar(self):
		""" Rutina típica de cerrar, cierra el MDI en focus y activa el
		focus del anterior """
		main.MDI.closeActiveSubWindow()
		main.MDI.activatePreviousSubWindow()
	
	def closeEvent(self, event):
		''' Evento que se activa cuando se cierra/destruye la clase en cuestion 
		se envía una alerta al usuario en caso afirmativo, se cierran todos los hijos,
		se corta la conexion correctamente con la base de datos '''
		result = QMessageBox.question(self,
		"Salir",
		"¿Está seguro que desea salir?",
		QMessageBox.Yes| QMessageBox.No)

		if result == QMessageBox.Yes:
			event.ignore()
			#DBL.Close()
			if self.GastOpen:
				self.GastOpen.close()
			if self.ComprOpen:
				self.ComprOpen.close()
			if self.VentOpen:	
				self.VentOpen.close()
			self.close()
			lock.release() #se libera el bloqueo
			event.accept()
		else:
			event.ignore()


""" Clases que administran las funciones del programa """

class Ventas(QWidget):
	''' Módulo de Ventas, donde se cargan y se vizualizan las ventas de la empresa '''

	def __init__(self):
		super(Ventas, self).__init__()
		loadUi('Ventas.ui', self)
		self.BCliente = False

		#Se declara validadores y se los aplica a distintos campos
		self.Line_Mes.setValidator(QRegExpValidator(QRegExp("\\b(0[1-9]|1[012])\\b")))
		self.Line_Ano.setValidator(QRegExpValidator(QRegExp("\\b(\\d{4})\\b")))
		self.L_Fact.setValidator(QRegExpValidator(QRegExp(
			"[0-9]{1,4}[-][0-9]{1,8}")))
		self.L_Fecha.setValidator(QRegExpValidator(QRegExp(
			"(0[1-9])|(1[0-9])|(2[0-9])|(3[0-1])")))
		val_num = QRegExpValidator(QRegExp("([0-9]+([.]{1}[0-9]{0,2})?[+]{1})+"))
		val_num1 = QRegExpValidator(QRegExp("^[0-9]{0,9}([\\.]{1}[0-9]{1,2})?"))
		self.L_Pan105.setValidator(val_num1)
		self.L_Pan21.setValidator(val_num1)
		self.L_Exento.setValidator(val_num)
		self.Line_Iva105.setValidator(val_num)
		self.Line_Iva21.setValidator(val_num)
		self.Line_OtrosN.setValidator(val_num1)
		self.Line_Total.setValidator(val_num1)

		#Se instalan los triggers de eventos a los campos correspondientes
		self.L_Fecha.installEventFilter(self)
		self.L_Comp.installEventFilter(self)
		self.L_Fact.installEventFilter(self)
		self.L_Pan105.installEventFilter(self)
		self.L_Pan21.installEventFilter(self)
		self.L_Exento.installEventFilter(self)
		self.Line_Iva105.installEventFilter(self)
		self.Line_Iva21.installEventFilter(self)
		self.Line_OtrosN.installEventFilter(self)
		self.Line_Total.installEventFilter(self)
		self.ActComp()

	##==============================================##
	def closeEvent(self, event):
		main.VentOpen = False
		try:
			self.sub.close()
		except:
			pass

	##==============================================##
	def ReadOnlytext(self, op):
		#Cambia el atributo "Read Only" de los campos en cuestión
		self.L_Fecha.setReadOnly(op)
		self.L_Fact.setReadOnly(op)
		self.L_Pan105.setReadOnly(op)
		self.L_Pan21.setReadOnly(op)
		self.L_Exento.setReadOnly(op)
		self.Line_Iva105.setReadOnly(op)
		self.Line_Iva21.setReadOnly(op)
		self.Line_OtrosN.setReadOnly(op)
		self.Line_Total.setReadOnly(op)

	##==============================================##
	""" Se habilitan todos los campos y secciones correspondientes cuando se
	se selecciona el boton 'Agregar' """

	def Agregar(self):
		self.BandMod = False
		self.G_Fact.setEnabled(True)
		self.L_Comp.setEnabled(True)
		self.G_Cliente.setEnabled(True)
		self.G_Dfact.setEnabled(True)
		self.B_Agregar.setEnabled(False)
		self.B_Grabar.setEnabled(True)
		self.B_Busc.setEnabled(True)
		self.Tabla_V.setEnabled(False)
		self.L_Fecha.setFocus()
		self.ReadOnlytext(False)

	##==============================================##
	# Instancia y abre el MDI para buscar clientes (F1)
	def showClient(self):
		self.sub = Busc_CliV(self)
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.sub.setWindowFlags(Qt.WindowCloseButtonHint)
		self.sub.show()
		self.sub.setFixedSize(self.sub.size())

	##==============================================##
	""" En pocas palabras, se juega con los focus
	en cada campo para que llame a la función correspondiente """

	def eventFilter(self, target, event):
		if event.type() == QEvent.FocusIn:
			if target == self.L_Pan105:
				self.Pan105in()
			elif target == self.L_Pan21:
				self.Pan21in()
			self.CalcTot()
		elif event.type() == QEvent.FocusOut and target != self.Line_Total:
			if target == self.L_Fecha:
				self.FecComp()
			elif target == self.L_Fact:
				self.FacComp()
			elif target == self.L_Pan105:
				self.Pan105out()
			elif target == self.L_Pan21:
				self.Pan21out()
			elif target == self.L_Exento:
				self.Exento()
			elif target == self.Line_Iva105 and not self.L_Pan105.text():
				self.Iva105()
			elif target == self.Line_Iva21 and	not self.L_Pan21.text():
				self.Iva21()
			elif target == self.Line_Iva105 and	self.L_Pan105.text():
				self.Iva105m()
			elif target == self.Line_Iva21 and	self.L_Pan21.text():
				self.Iva21m()
			elif target == self.Line_OtrosN:
				self.IvaOtrosC()
			self.CalcTot()
		return False

	##==============================================##
	# Todas las funciones que se llaman desde los eventos de arriba.
	def FecComp(self):
		'''Se autocompleta la fecha con el día ingresado,
		se toma el periodo anteriormente buscado '''

		if self.L_Fecha.text() and self.L_Fecha.hasAcceptableInput():
			aux = (self.L_Fecha.text() + '-'
				+ self.Line_Mes.text() + '-' + self.Line_Ano.text())
			self.L_Fecha.setText(aux)
		elif self.L_Fecha.text() and len(self.L_Fecha.text()) <= 2:
			self.L_Fecha.clear()
			self.L_Fecha.setFocus()

	def FacComp(self):
		''' Agregando el pto de venta el guion y el nro de facutra
		se rellena con los ceros necesarios para completarlo '''

		if self.L_Fact.text() and self.L_Fact.hasAcceptableInput():
			aux = self.L_Fact.text().split('-')
			aux1 = aux[0].zfill(4)
			aux = aux[1].zfill(8)
			self.L_Fact.setText(str(aux1 + '-' + aux))
		else:
			self.L_Fact.clear()

	def Pan105in(self):
		if self.Line_Iva105.text() and not self.L_Pan105.isReadOnly():
			val = round(float(self.Line_Iva105.text()) / float(0.105), 2)
			self.L_Pan105.setText('{:.2f}'.format(val))
		else:
			self.L_Pan105.setText('0.00')
		self.CalcTot()

	def Pan105out(self):
		if self.Line_Iva105.text() and not self.L_Pan105.isReadOnly():
			try:
				self.L_Pan105.setText('{:.2f}'.format(round(float(self.L_Pan105.text()), 2)))
			except:
				self.L_Pan105.setText('0.00')
		self.CalcTot()

	def Pan21in(self):
		if self.Line_Iva21.text() and not self.L_Pan21.isReadOnly():
			val = round(float(self.Line_Iva21.text()) / float(0.21), 2)
			self.L_Pan21.setText('{:.2f}'.format(val))
		else:
			self.L_Pan21.setText('0.00')
		self.CalcTot()

	def Pan21out(self):
		if self.Line_Iva21.text() and not self.L_Pan21.isReadOnly():
			try:
				self.L_Pan21.setText('{:.2f}'.format(round(float(self.L_Pan21.text()), 2)))
			except:
				self.L_Pan21.setText('0.00')
		self.CalcTot()

	def Exento(self):
		try:
			if self.L_Exento.text():
				texto = self.L_Exento.text()
				if texto[-1] == '+':
					texto = texto[:-1]
					self.L_Exento.setText('{:.2f}'.format(texto))
		finally:
			if self.L_Exento.text() and not self.L_Exento.isReadOnly():
				values = [float(val) for val in self.L_Exento.text().split("+")]
				self.L_Exento.setText('{:.2f}'.format(round(sum(values), 2)))
			else:
				self.L_Exento.setText('0.00')
		self.CalcTot()

	def Iva105(self):
		try:
			if self.Line_Iva105.text():
				texto = self.Line_Iva105.text()
				if texto[-1] == '+':
					texto = texto[:-1]
					self.Line_Iva105.setText('{:.2f}'.format(texto))
		finally:
			if self.Line_Iva105.text() and not self.Line_Iva105.isReadOnly():
				values = [float(val) for val in self.Line_Iva105.text().split("+")]
				self.Line_Iva105.setText('{:.2f}'.format(round(sum(values), 2)))
			else:
				self.Line_Iva105.setText('0.00')
		self.CalcTot()

	def Iva21(self):
		try:
			if self.Line_Iva21.text():
				texto = self.Line_Iva21.text()
				if texto[-1] == '+':
					texto = texto[:-1]
					self.Line_Iva21.setText('{:.2f}'.format(texto))
		finally:
			if self.Line_Iva21.text() and not self.Line_Iva21.isReadOnly():
				values = [float(val) for val in self.Line_Iva21.text().split("+")]
				self.Line_Iva21.setText('{:.2f}'.format(round(sum(values), 2)))
			else:
				self.Line_Iva21.setText('0.00')
			self.CalcTot()

	def Iva21m(self):
		if self.Line_Iva21.text():
			self.Line_Iva21.setText('{:.2f}'.format(round(float(self.Line_Iva21.text()) ,2)))
		self.CalcTot()

	def Iva105m(self):
		if self.Line_Iva105.text():
			self.Line_Iva105.setText('{:.2f}'.format(round(float(self.Line_Iva105.text()) ,2)))
		self.CalcTot()

	def IvaOtrosC(self):
		if self.Line_OtrosN.text():
			self.Line_OtrosN.setText('{:.2f}'.format(
				round(float(self.Line_OtrosN.text()), 2)))
		else:
			self.Line_OtrosN.setText('0.00')
		self.CalcTot()

	def CalcTot(self):
		'''Se calcula todos los campos y se lo inserta formateado
		en el campo total si alguno faltara y entraría por el error
		y no haría nada.'''
		
		try:
			if not self.Line_Total.isReadOnly():
				aux = round((float(self.L_Pan105.text()) + float(
					self.L_Pan21.text()) + float(
					self.L_Exento.text()) +	float(
					self.Line_Iva105.text()) + float(
					self.Line_Iva21.text()) + float(
					self.Line_OtrosN.text())), 2)
				self.Line_Total.setText('{:.2f}'.format(aux))
		except ValueError:
			return

	##==============================================##
	def Grabar(self):
		''' Se formatea todos los valores y se verifican que esten correctos
		antes de ingresarlos a la BD para tenes una normalización '''
		
		try:
			Fecha = datetime.strptime(
				self.L_Fecha.text(), "%d-%m-%Y").strftime("%Y-%m-%d")
			Comp = self.L_Comp.currentText()
			Fact = self.L_Fact.text()
			Cuit = self.L_Doc.text()
			Pan105 = '{:.2f}'.format(float(self.L_Pan105.text()))
			Pan21 = '{:.2f}'.format(float(self.L_Pan21.text()))
			Exe = '{:.2f}'.format(float(self.L_Exento.text()))
			Iva105 = '{:.2f}'.format(float(self.Line_Iva105.text()))
			Iva21 = '{:.2f}'.format(float(self.Line_Iva21.text()))
			Otros = '{:.2f}'.format(float(self.Line_OtrosN.text()))
			Tot = '{:.2f}'.format(float(self.Line_Total.text()))
			
			""" Se usa una bandera para saber si es una
			nueva factura o una actualizacion de alguna existente, luego se pregunta si es una
			nota de credito para agregar los correspondientes negativos, si hay error
			se informa al usuario en todos los casos de crean logs del error por cualquier problema """
			if not self.BandMod:
				if Comp in ['Ncred. A', 'Ncred. B']:
					Query = "INSERT INTO ventas(Fecha, Comprobante, N_fact, Cuit, Pan105, \
						Pan21, Exento, Iva105, Iva21, Otros, Total) \
						VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', \
						'%s', '%s', '%s')" % (Fecha, Comp, Fact, Cuit,
							'-' + Pan105, '-' + Pan21, '-' + Exe,
							'-' + Iva105, '-' + Iva21, '-' + Otros, '-' + Tot)
				else:
					Query = "INSERT INTO ventas(Fecha, Comprobante, N_fact, Cuit, Pan105, \
						Pan21, Exento, Iva105, Iva21, Otros, Total) \
						VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',\
						'%s', '%s', '%s')" % (Fecha, Comp, Fact, Cuit,
						Pan105, Pan21, Exe, Iva105, Iva21, Otros, Tot)
			else:
				if Comp in ['Ncred. A', 'Ncred. B']:
					if Pan105[0] != '-':
						Pan105 = '-' + Pan105
					if Pan21[0] != '-':
						Pan21 = '-' + Pan21
					if Exe[0] != '-':
						Exe = '-' + Exe
					if Iva105[0] != '-':
						Iva105 = '-' + Iva105
					if Iva21[0] != '-':
						Iva21 = '-' + Iva21
					if Otros[0] != '-':
						Otros = '-' + Otros
					if Tot[0] != '-':
						Tot = '-' + Tot
				Query = "UPDATE ventas SET Fecha = '%s', Comprobante = '%s', \
				N_fact = '%s',Cuit = '%s', Pan105 = '%s', \
				Pan21 = '%s', Exento = '%s', Iva105 = '%s', \
				Iva21 = '%s', Otros = '%s', Total = '%s' \
				WHERE Comprobante LIKE '%s' AND N_fact LIKE '%s' AND Cuit LIKE '%s'" \
				% (Fecha, Comp, Fact, Cuit, Pan105, Pan21, Exe, Iva105, Iva21,
					Otros, Tot, self.compT, self.factT, self.cuitT)
			DBL.Queryone(Query)

			main.statusBar.showMessage("Grabado correcto", 5000)
			main.statusBar.setStyleSheet("color: rgb(0, 85, 0)")
			self.Borrar()
			self.B_Periodo()
			self.ReadOnlytext(True)
		except mysql.connector.IntegrityError:
			main.statusBar.showMessage("Error, factura existente", 5000)
			main.statusBar.setStyleSheet("color: rgb(170, 0, 0)")
			main.CrearLogs()
		except:
			main.statusBar.showMessage("Error en los datos ingresados", 5000)
			main.statusBar.setStyleSheet("color: rgb(170, 0, 0)")
			main.CrearLogs()

	##==============================================##
	def Borrar(self):
		self.Tabla_V.blockSignals(True)
		self.ReadOnlytext(True)
		self.L_Fecha.clear()
		self.L_Fact.clear()
		self.L_Comp.setCurrentIndex(0)
		self.L_Nomb.clear()
		self.L_Doc.clear()
		self.L_Pan105.clear()
		self.L_Coment.clear()
		self.L_Pan21.clear()
		self.L_Exento.clear()
		self.Line_Iva105.clear()
		self.Line_Iva21.clear()
		self.Line_OtrosN.clear()
		self.Line_Total.clear()
		self.B_Agregar.setEnabled(True)
		self.B_Anular.setEnabled(False)
		self.B_Mod.setEnabled(False)
		self.B_Grabar.setEnabled(False)
		self.B_Busc.setEnabled(False)
		self.Tabla_V.setCurrentCell(-1, -1)
		self.L_FactC.clear()
		self.L_Imptot.clear()
		if self.G_Cliente.isEnabled():
			self.G_Fact.setEnabled(False)
			self.G_Cliente.setEnabled(False)
			self.G_Dfact.setEnabled(False)
			self.Tabla_V.setEnabled(True)
		else:
			self.Tabla_V.setEnabled(False)
			self.Tabla_V.setRowCount(0)
			self.Tabla_V.setColumnCount(0)
			self.frame.setEnabled(True)
			self.Line_Mes.clear()
			self.Line_Ano.clear()
			self.B_Agregar.setEnabled(False)
			self.Line_Mes.setFocus()
			self.L_Coment.clear()
		self.Tabla_V.blockSignals(False)

	##==============================================##
	#Pobliacion de los campos desplegable
	def ActComp(self):
		self.L_Comp.clear()
		rows = DBL.Queryall("SELECT Descripcion FROM comprobantes")
		for row in rows:
			self.L_Comp.addItem(str(row[0]))

	##==============================================##
	''' Busqueda del periodo ingresado, se verifica que el año y mes esten completos '''
	def B_Periodo(self):
		if self.Line_Mes.hasAcceptableInput() and self.Line_Ano.hasAcceptableInput():
			self.Tabla_V.setRowCount(0)
			self.Tabla_V.setColumnCount(4)
			self.Tabla_V.setHorizontalHeaderLabels(['Fecha',
				'Tipo', 'Factura', 'Total'])
			self.Tabla_V.setColumnWidth(0, 85)
			self.Tabla_V.setColumnWidth(1, 65)
			self.Tabla_V.setColumnWidth(2, 100)
			self.Tabla_V.setColumnWidth(3, 75)
			self.Tabla_V.horizontalHeader().setStretchLastSection(True)

			Query = "SELECT Fecha, Comprobante, N_fact, Total FROM ventas \
				WHERE YEAR(Fecha) = '%s' AND MONTH(Fecha) = '%s' \
				ORDER BY Fecha, N_fact" % (self.Line_Ano.text(), self.Line_Mes.text())
			rows = DBL.Queryall(Query)
			i = 0
			for row in rows:
				self.Tabla_V.insertRow(i)
				self.Tabla_V.setItem(i, 0,
					main.CrearItem(row[0].strftime("%d-%m-%Y"), 10, 'RS'))
				self.Tabla_V.setItem(i, 1, main.CrearItem(row[1], 10, 'RS'))
				self.Tabla_V.setItem(i, 2, main.CrearItem(row[2], 10, 'RS'))
				self.Tabla_V.setItem(i, 3, main.CrearItem(locale.format_string(
				'%10.2f', float(row[3])), 10, 'RS'))
				i += 1
			self.Tabla_V.resizeRowsToContents()
			self.Tabla_V.setEnabled(True)
			self.B_Agregar.setEnabled(True)
			self.frame.setEnabled(False)
			self.G_Fact.setEnabled(False)
			self.G_Cliente.setEnabled(False)
			self.G_Dfact.setEnabled(False)
			self.B_Grabar.setEnabled(False)
			self.B_Busc.setEnabled(False)

	##==============================================##
	def SelectFact(self, rowx, column):
		''' Se busca la factura en cuestion seleccionada y
		se rellena los campos con la misma '''
		self.L_Coment.clear()
		self.B_Mod.setEnabled(True)
		self.B_Anular.setEnabled(True)
		self.G_Fact.setEnabled(True)
		self.G_Cliente.setEnabled(True)
		self.G_Dfact.setEnabled(True)
		self.L_Comp.setEnabled(False)
		self.B_Agregar.setEnabled(False)
		fecha = self.Tabla_V.item(rowx, 0).text()
		fecha = datetime.strptime(fecha, "%d-%m-%Y").strftime("%Y-%m-%d")
		self.compT = self.Tabla_V.item(rowx, 1).text()
		self.factT = self.Tabla_V.item(rowx, 2).text()

		Query = "SELECT * FROM ventas WHERE Fecha = '%s' AND Comprobante = '%s' \
			AND N_fact = '%s'" % (fecha, self.compT, self.factT)
		row = DBL.Queryone(Query)

		self.L_Fecha.setText(row[0].strftime("%d-%m-%Y"))
		self.L_Comp.setCurrentIndex(self.L_Comp.findText(row[1]))

		self.L_Fact.setText(row[2])
		Query = "SELECT RazonS FROM clientes WHERE Cuit LIKE '%s' " % (row[3])
		row1 = DBL.Queryone(Query)

		self.L_Nomb.setText(row1[0])
		self.L_Doc.setText(row[3])
		self.L_Pan105.setText(row[4])
		self.L_Pan21.setText(row[5])
		self.L_Exento.setText(row[6])
		self.Line_Iva105.setText(row[7])
		self.Line_Iva21.setText(row[8])
		self.Line_OtrosN.setText(row[9])
		self.Line_Total.setText(row[10])
		self.cuitT = row[3]

	##==============================================##
	def ModFact(self):
		''' Se prepara la UI para la modificacion de una factura '''
		self.BandMod = True
		self.B_Mod.setEnabled(False)
		self.B_Anular.setEnabled(False)
		self.G_Fact.setEnabled(True)
		self.L_Comp.setEnabled(True)
		self.G_Cliente.setEnabled(True)
		self.G_Dfact.setEnabled(True)
		self.B_Agregar.setEnabled(False)
		self.B_Grabar.setEnabled(True)
		self.B_Busc.setEnabled(True)
		self.Tabla_V.setEnabled(False)
		self.ReadOnlytext(False)
		self.L_Comp.setEnabled(True)
		self.L_Fecha.setFocus()

	##==============================================##
	def Cerrar(self):
		self.close()

	##==============================================##
	def AnularFact(self):
		''' La anulación de una factura es una convención que se ´habló
		con el cliente ya que esto no es legal, pero si lo es cuando son 
		facturas por imprenta, simplemente se cambia el cliente a ANULADO
		se vuelve a 0.00 todos los importes '''

		if self.L_Comp.currentText() == 'Fact.A':
			result = QMessageBox.question(self,
			"Anular Factura",
			"¿Está seguro que desea anular esta factura?",
			QMessageBox.Yes| QMessageBox.No)

			if result == QMessageBox.Yes:
				Query = "UPDATE ventas SET Cuit = '%s', Pan105 = '%s', \
					Pan21 = '%s', Exento = '%s', Iva105 = '%s', \
					Iva21 = '%s', Otros = '%s', Total = '%s' \
					WHERE Comprobante LIKE '%s' AND N_fact LIKE '%s' AND Cuit LIKE '%s'" \
					% ('99-99999999-9', '0.00', '0.00', '0.00', '0.00', '0.00',
						'0.00', '0.00', 'Fact.A', self.L_Fact.text(), self.L_Doc.text())
				DBL.Queryone(Query)
				
				Query = "DELETE FROM venta_productos WHERE N_fact LIKE '%s'" % self.L_Fact.text()
				DBL.Queryone(Query)

				self.Borrar()
				self.B_Periodo()
		else:
			VentanaPrincipal.showAlerta(self, 1, 'Solo se pueden anular facturas A')

	##==============================================##
	def Calc_Fact(self):
		#Se calcula el total de facturas e importe del periodo ingresado
		if self.Line_Ano.text() and self.Line_Mes.text():
			Query = "SELECT COUNT(*), SUM(Total) FROM ventas WHERE YEAR(Fecha) = '%s'\
				AND MONTH(Fecha) = '%s'" % (self.Line_Ano.text(), self.Line_Mes.text())
			row = DBL.Queryone(Query)

			self.L_FactC.setText(str(row[0]))
			if row[1] is None:
				self.L_Imptot.setText('0,00')
			else:
				self.L_Imptot.setText(locale.format_string('%10.2f', round(row[1], 2), grouping=True))

class Busc_CliV(QWidget):
	''' MDI de busqueda de clintes '''

	def __init__(self, parent):
		super(Busc_CliV, self).__init__()
		loadUi('B_Clientes.ui', self)
		#Se guarda en una variable el widget del padre para poder enviarle información. 
		#Digamos que es un puntero, este razonamiento se utliza en todos los casos.
		self.padre = parent

	##==============================================##
	def Cerrar(self):
		self.close()

	def closeEvent(self, event):
		self.padre.BCliente = False

	##==============================================##
	def QueryClientes(self):
		self.Tabla_Clientes.setRowCount(0)
		self.Tabla_Clientes.setColumnCount(1)
		self.Tabla_Clientes.setHorizontalHeaderLabels(['Razón Social'])
		i = 0
		Name = self.Line_Cliente.text()

		if self.R_Razon.isChecked():
			Query = "SELECT RazonS FROM clientes WHERE RazonS LIKE \
				concat('%%','%s','%%')" % Name
		elif self.R_Cuit.isChecked():
			Query = "SELECT RazonS FROM clientes WHERE Cuit LIKE \
				concat('%%','%s','%%')" % Name
		elif self.R_Alias.isChecked():
			Query = "SELECT RazonS FROM proveedores WHERE Alias LIKE \
				concat('%%','%s','%%')" % Name
		rows = DBL.Queryall(Query)

		for row in rows:
			self.Tabla_Clientes.insertRow(i)
			self.Tabla_Clientes.setItem(i, 0, main.CrearItem(str(row[0]), 10, 'RS'))
			i = + 1
		self.Tabla_Clientes.resizeRowsToContents()
		self.Tabla_Clientes.sortItems(0, order=Qt.AscendingOrder)

	##==============================================##
	def Resultados(self, row, column):
		Name = self.Tabla_Clientes.item(row, column).text()

		Query = "SELECT Cuit,RazonS FROM clientes \
			WHERE RazonS LIKE '%s'" % Name
		row = DBL.Queryone(Query)

		self.padre.L_Nomb.setText(row[1])
		self.padre.L_Doc.setText(row[0])
		self.close()


class Precios(QWidget):
	""" Clase que administra los precios de los productos segun una lista se comentaron las lineas q
		que se utilizan para otra parte de la base de datos que no esta disponible aqui."""

	def __init__(self):
		super(Precios, self).__init__()
		loadUi('Precios.ui', self)
		self.Inicializar()
		self.installEventFilter(self)
	
	##==============================================##
	def eventFilter(self, target, event):
		if event.type() == QEvent.KeyPress \
			and event.key() == Qt.Key_Escape:
			self.Inicializar()
		return False
	
	##==============================================##
	def Salir(self):
		VentanaPrincipal.Cerrar(self)

	def closeEvent(self, event):
		main.PrecOpen = False
	
	##==============================================##
	def Buscar(self):
		self.C_Lista.setEnabled(False)
		self.Lista = self.C_Lista.currentText()
		self.Search()
		self.Line_B.setEnabled(True)
		self.B_Buscar.setEnabled(False)
		self.R_Negocio.setEnabled(False)
		self.R_Camio.setEnabled(False)

	##==============================================##
	def Inicializar(self):
		self.C_Lista.clear()
		self.Line_B.clear()
		self.C_Lista.setEnabled(True)
		self.B_Buscar.setEnabled(True)
		self.Line_B.setEnabled(False)
		rows = DBL.Queryall("SELECT * FROM listas")
		for row in rows:
			self.C_Lista.addItem(str(row[1]))
		self.T_Lista.setColumnCount(3)
		self.T_Lista.setColumnWidth(0,200)
		self.T_Lista.setColumnWidth(1,80)
		self.T_Lista.setCurrentCell(-1, 1)
		self.T_Lista.setRowCount(0)	
		self.T_Lista.horizontalHeader().setStretchLastSection(True)
		self.T_Lista.setHorizontalHeaderLabels(['Nombre', 'Precio', 'Fecha Act.'])
		self.R_Negocio.setEnabled(True)
		self.R_Camio.setEnabled(True)
		self.R_Negocio.setChecked(True)

	##==============================================##
	def SetValor(self, item):
		if item.column() == 1:
			self.Precio = item.tableWidget().item(item.row(), 1).text()

	##==============================================##
	def SavePrecio(self, item):
		if item.column() == 1:
			self.T_Lista.blockSignals(True)
			try:
				Nombre = item.tableWidget().item(item.row(), 0).text()
				Lista =	self.C_Lista.currentText()
				Fecha = date.today().strftime("%d-%m-%Y")
				if self.R_Negocio.isChecked():
					Query = "UPDATE productos SET Precio = '%s', Fecha = '%s' \
						WHERE Lista = '%s' AND Nombre = '%s' " % ('{:.4f}'.format(float(item.text())), date.today(), Lista, Nombre)
				#else:
				#	Query = "UPDATE %s.productos SET Precio = '%s', Fecha = '%s' \
				#		WHERE Lista = '%s' AND Nombre = '%s' " % (self.camioneta, 
				#		'{:.4f}'.format(float(item.text())), date.today(), Lista, Nombre)
				DBL.Queryone(Query)
				item.tableWidget().item(item.row(), 1).setText('{:.4f}'.format(float(item.text())))
				item.tableWidget().item(item.row(), 2).setText(Fecha)
			except:
				VentanaPrincipal.showAlerta(self, 1, 'Valor invalido')
				item.tableWidget().item(item.row(), 1).setText(self.Precio)
			self.T_Lista.blockSignals(False)
	
	##==============================================##
	def Search(self, texto = ''):
		self.T_Lista.setRowCount(0)
		if self.R_Negocio.isChecked():
			Query = "SELECT Nombre, Precio, Fecha FROM productos WHERE \
				Lista = '%s' AND Nombre LIKE '%%%s%%'" % (self.Lista, texto)
		#else:
		#	Query = "SELECT Nombre, Precio, Fecha FROM %s.productos WHERE \
		#		Lista = '%s' AND Nombre LIKE '%%%s%%'" % (self.camioneta, self.Lista, texto)
		rows = DBL.Queryall(Query)
		self.T_Lista.blockSignals(True)
		for row in rows:
			self.T_Lista.insertRow(self.T_Lista.rowCount())
			self.T_Lista.setItem(self.T_Lista.rowCount()-1, 0, main.CrearItem(str(row[0]), 9, 'R'))
			self.T_Lista.setItem(self.T_Lista.rowCount()-1, 1, main.CrearItem(str(row[1]), 10, 'T'))
			self.T_Lista.setItem(self.T_Lista.rowCount()-1, 2, main.CrearItem(row[2].strftime("%d-%m-%Y"), 10, 'R'))
		self.T_Lista.resizeRowsToContents()
		self.T_Lista.blockSignals(False)
	
	##==============================================##
	def SetLista(self):
		self.C_Lista.clear()
		if self.R_Negocio.isChecked():
			rows = DBL.Queryall("SELECT * FROM listas")
		#else:
		#	rows = DBL.Queryall("SELECT * FROM %s.listas" % self.camioneta)
			for row in rows:
				self.C_Lista.addItem(str(row[1]))


class SplashScreen(QWidget):
	def __init__(self):
		super().__init__()
		loadUi('Splash.ui', self)
		self.setWindowFlag(Qt.FramelessWindowHint)

		self.counter = 0
		self.n = 80

		self.progressBar.setRange(0, self.n)

		self.timer = QTimer()
		self.timer.timeout.connect(self.Carga)
		self.timer.start(30)

	def Carga(self):
		self.progressBar.setValue(self.counter)

		if self.counter == int(self.n * 0.3):
			self.labelDescription.setText('Decorando tortas ...')
		elif self.counter == int(self.n * 0.6):
			self.labelDescription.setText('Comiendo algunas facturas ...')
		elif self.counter >= self.n:
			self.timer.stop()
			self.close()

			time.sleep(1)

			global main
			main.show()

		self.counter += 1




""" Unicamente disponible las funciones Ventas y Precios (que se encuentra en la pestaña Productos) """


""" Ejecucion del programa 
	- Se crea un archivo .lock que no se borra hasta 
		que no se cierra el programa
	- Si el archivo está creado, no se podrá abrir otra instancia del programa,
		por lo tanto se llamará al except. Donde se notifica.
	- Se cuenta con un directorio temporal para algunas cosas del programa,
		para no "ensuciar" la carpeta raiz. """
app = QApplication(sys.argv)

lock = FileLock("Temp.txt.lock") #archivo de bloqueo
try:
	with lock.acquire(timeout=2):
		file = QFile("Aqua.qss") #Plantilla para cosas visuales.
		file.open(QFile.ReadOnly | QFile.Text)
		stream = QTextStream(file)
		app.setStyleSheet(stream.readAll())
		main = VentanaPrincipal()
		main.statusBar.setFont(QFont('Yu Gothic', 10, QFont.Bold)) #Formateo la letra del StatusBar
		config = configparser.ConfigParser()
		config.read('config.ini') #Leo la config. del .ini
		DBL = DbLocal() #Se instancia BD
		path = os.path.dirname(sys.argv[0]) #Se pone una variable, el puntero donde se encuentra la carpeta raiz del programa.
		splash = SplashScreen()
		splash.show() #Se muestra el loading splash, totalmente decorativo, la idea fue dejarlo preparado para procesos secundarios en un futuro. Al cliente le agrada estas cosas
		sys.exit(app.exec_())
except Timeout:
	VentanaPrincipal.showAlerta(app, 1, 'Ya está en ejecucion el programa') #Si el bloqueo persiste luego del timeout, se alerta al usuario y el programa finaliza
except mysql.connector.Error as err:
	if err.errno == 1045: #Error de autentificacion.
		VentanaPrincipal.showAlerta(app, 1, 'Error de autentificacion en la base de datos', 'No se pudo establecer conexión')	
	else:
		VentanaPrincipal.showAlerta(app, 1, str(err)) #si es un error distinto de base de datos., se muestra por pantalla el error.
except Exception as e:
	VentanaPrincipal.CrearLogs(app) #si es otro tipo de error, se crea un archivo .log con el error en carpeta raiz.




""" Creado por: Gonzalez Magaldi, Juan Pablo. 
	Derechos reservados 2022. 
	Prohibido su uso sin autorizacion,	ni su edición """