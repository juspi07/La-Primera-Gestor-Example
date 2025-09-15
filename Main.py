import os, sys, mysql.connector, configparser, locale, time, tempfile, traceback, fileinput
from datetime import datetime, date
from PyQt5.QtCore import Qt, QRegExp, QEvent, QTimer
from PyQt5.QtGui import QFont, QRegExpValidator, QIcon, QPixmap
from PyQt5.QtWidgets import QTableWidgetItem, QMainWindow, QMdiSubWindow, QWidget, QApplication, QMessageBox
from filelock import FileLock, Timeout
from pathlib import Path
from Ui.VentanaPrincipal_ui import Ui_VentanaPrincipal
from Ui.Ventas_ui import Ui_Ventas
from Ui.B_Clientes_ui import Ui_B_Clientes
from Ui.Clientes_ui import Ui_ABMCli
from Ui.Precios_ui import Ui_Precios
from Ui.Splash_ui import Ui_Splash




def resource_path(relative_path):
	""" Obtenemos la ruta absoluta al recurso """
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	return os.path.join(base_path, relative_path)


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
class VentanaPrincipal(Ui_VentanaPrincipal, QMainWindow):
	""" Clase principal, contenedora de todas las demás clases"""
	
	def __init__(self):
		super(VentanaPrincipal, self).__init__()
		self.setupUi(self)
		self.setContextMenuPolicy(Qt.NoContextMenu)
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.Ini_SubWindows()
		self.SeteoIconos()

	def SeteoIconos(self):	
		self.setWindowIcon(QIcon(ico_dir + "\\Icon.ico"))
		self.Venta.setIcon(QIcon(ico_dir + "\\Venta.png"))
		self.Gastos.setIcon(QIcon(ico_dir + "\\Gastos.png"))
		self.Compras.setIcon(QIcon(ico_dir + "\\Compras.png"))
		self.Clientes.setIcon(QIcon(ico_dir + "\\Clientes.png"))
		self.Proveedores.setIcon(QIcon(ico_dir + "\\Proveedor.png"))
		self.Tablas.setIcon(QIcon(ico_dir + "\\Tablas.png"))
		self.Rankings.setIcon(QIcon(ico_dir + "\\Rankings.png"))
		self.Cuentas.setIcon(QIcon(ico_dir + "\\Cuentas.png"))
		self.Generar.setIcon(QIcon(ico_dir + "\\Zonas.png"))
		self.Recibos.setIcon(QIcon(ico_dir + "\\Recibo.png"))
		self.Salir.setIcon(QIcon(ico_dir + "\\Salir.png"))
		#Unicamente para restringir el uso, ya que no estan implementadas
		for target in [self.Gastos, self.Compras,
			self.Proveedores, self.Tablas,
			self.Rankings, self.Cuentas, self.Generar,
			self.Recibos, self.menuFabrica, self.menuFacturacion]:
			target.setEnabled(False)
	
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
		self.VentOpen = self.PrecOpen = False
		self.ClienOpen = False

	##==============================================##
	def CrearLogs(self):
		""" Crea o agrega a un logs.txt (en carpeta raíz) la informacion del error """
		f = open(os.path.expanduser('~\\log.txt'), "a")
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

	def showPrecios(self):
		if not self.PrecOpen:
			self.PrecOpen = self.AbrirMDI(Precios())
		else:
			self.MDI.setActiveSubWindow(self.PrecOpen)

	def showClientes(self):
		if not self.ClienOpen:
			self.ClienOpen = self.AbrirMDI(Clientes())
		else:
			self.MDI.setActiveSubWindow(self.ClienOpen)

	def showVentas(self):
		if not self.VentOpen:
			sub = Ventas()
			sub.setAttribute(Qt.WA_DeleteOnClose)
			sub.setWindowFlags(Qt.WindowCloseButtonHint)
			sub.show()
			self.VentOpen = sub

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
			try:
				DBL.Close()
				if self.VentOpen:	
					self.VentOpen.close()
				self.close()
				os.remove(resource_path('Aqua.qss'))
				os.rename(resource_path('Aqua.qss.bak'), resource_path('Aqua.qss'))
				lock.release() #se libera el bloqueo
				event.accept()
			except:
				VentanaPrincipal.CrearLogs(self)
		else:
			event.ignore()


""" Clases que administran las funciones del programa """

class Ventas(QWidget, Ui_Ventas):
	''' Módulo de Ventas, donde se cargan y se vizualizan las ventas de la empresa '''

	def __init__(self):
		super(Ventas, self).__init__()
		self.setupUi(self)
		self.setWindowIcon(QIcon(ico_dir + "\\Icon.ico"))
		self.BCliente = False
		self.Line_Total.setReadOnly(True)

		#Se declara validadores y se los aplica a distintos campos
		self.Line_Mes.setValidator(
			QRegExpValidator(QRegExp("\\b(0[1-9]|1[012])\\b")))
		self.Line_Ano.setValidator(
			QRegExpValidator(QRegExp("\\b(\\d{4})\\b")))
		self.L_Fact.setValidator(QRegExpValidator(QRegExp(
			"[0-9]{1,5}[-][0-9]{1,8}")))
		self.L_Fecha.setValidator(QRegExpValidator(QRegExp(
			"(0[1-9])|(1[0-9])|(2[0-9])|(3[0-1])")))
		val_num = QRegExpValidator(
			QRegExp("([0-9]+([.]{1}[0-9]{0,2})?[+]{1})+"))
		val_num1 = QRegExpValidator(
			QRegExp("^[0-9]{0,9}([\\.]{1}[0-9]{1,2})?"))
		self.L_Pan105.setValidator(val_num1)
		self.L_Pan21.setValidator(val_num1)
		self.L_Exento.setValidator(val_num)
		self.Line_Iva105.setValidator(val_num)
		self.Line_Iva21.setValidator(val_num)
		self.Line_OtrosN.setValidator(val_num1)

		#Se instalan los triggers de eventos a los campos correspondientes
		targets = [self.L_Fecha, self.L_Comp, self.L_Fact, self.L_Pan105,
			self.L_Pan21, self.L_Exento, self.Line_Iva105, self.Line_Iva21,
			self.Line_OtrosN]
		for target in targets:
			target.installEventFilter(self)

		self.ActComp()
		self.frame_2.setEnabled(False)
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
			match target:
				case self.L_Pan105:
					val = round(float(self.Line_Iva105.text()) / float(0.105), 2)
					target.setText('{:.2f}'.format(val))
				case self.L_Pan21:
					val = round(float(self.Line_Iva21.text()) / float(0.21), 2)
					target.setText('{:.2f}'.format(val))
			self.CalcTot()
		elif event.type() == QEvent.FocusOut:
			match target:
				case self.L_Fecha:
					if target.text():
						if target.hasAcceptableInput():
							aux = target.text() + '-' + self.Line_Mes.text() \
							+ '-' + self.Line_Ano.text()
							target.setText(aux)
						elif len(target.text()) <= 2:
							target.clear()
							target.setFocus()
				case self.L_Fact:
					if target.text() and target.hasAcceptableInput():
						aux = target.text().split('-')
						aux1 = aux[0].zfill(5)
						aux = aux[1].zfill(8)
						target.setText(aux1 + '-' + aux)
					else:
						target.clear()			
				case self.L_Pan105:
					self.L_Pan105.setText('{:.2f}'.format(round(float(self.L_Pan105.text()), 2)))
				case self.L_Pan21:
					self.L_Pan21.setText('{:.2f}'.format(round(float(self.L_Pan21.text()), 2)))
				case _ if target in [self.L_Exento, self.Line_OtrosN]:
					if target.text():
						target.setText('{:.2f}'.format(
							round(float(target.text()), 2)))
					else:
						target.setText('0.00')
				case self.Line_Iva105:
					try:
						target.setText('{:.2f}'.format(float(target.text())))
					except:
						target.setText('0.00')
				case self.Line_Iva21:
					try:
						target.setText('{:.2f}'.format(float(target.text())))
					except:
						target.setText('0.00')
			self.CalcTot()
		return False

	##==============================================##
	def CalcTot(self):
		'''Se calcula todos los campos y se lo inserta formateado
		en el campo total si alguno faltara y entraría por el error
		y no haría nada.'''
		
		try:
			#if not self.Line_Total.isReadOnly():
			aux = round((float(self.L_Pan105.text()) + float(
				self.L_Pan21.text()) + float(
				self.L_Exento.text()) +	float(
				self.Line_Iva105.text()) + float(
				self.Line_Iva21.text()) + float(
				self.Line_OtrosN.text())), 2)
			self.Line_Total.setText(locale.currency(aux, grouping=True, symbol=False))
		except ValueError:
			return

	##==============================================##
	def Eliminar(self):
		self.Tabla_V.blockSignals(True)
		comp = self.Tabla_V.item(self.Tabla_V.currentRow(),
			1).text()
		fact = self.Tabla_V.item(self.Tabla_V.currentRow(),
			2).text()
		Query = "DELETE FROM Ventas WHERE N_fact LIKE '%s' \
			AND Comprobante LIKE '%s'" % (fact, comp)
		DBL.Execute(Query)
		main.statusBar.showMessage("Borrado correcto", 5000)
		main.statusBar.setStyleSheet("color: rgb(0, 85, 0)")
		self.Borrar()
		self.B_Periodo()
		self.Tabla_V.blockSignals(False)
	
	##==============================================##	
	def Verificacion(self):
		if self.L_Fact.hasAcceptableInput() and \
			self.Line_Total.text() and self.L_Doc.text() and \
			self.L_Fecha.text():
			return True
		else:
			return False

	##==============================================##
	def Grabar(self):
		''' Se formatea todos los valores y se verifican que esten correctos
		antes de ingresarlos a la BD para tenes una normalización '''
		
		try:
			if self.Verificacion():
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
				Tot = (self.Line_Total.text().replace('.','')).replace(',','.')
				
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
				DBL.Execute(Query)

				main.statusBar.showMessage("Grabado correcto", 5000)
				main.statusBar.setStyleSheet("color: rgb(0, 85, 0)")
				self.Borrar()
				self.B_Periodo()
				self.ReadOnlytext(True)
			else:
				main.statusBar.showMessage("Error, datos faltantes", 5000)
				main.statusBar.setStyleSheet("color: rgb(170, 0, 0)")
		
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
		self.B_Elim.setEnabled(False)
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
			self.frame_2.setEnabled(False)
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
		if self.Line_Mes.setText(self.Line_Mes.text().zfill(2)) == '00':
			self.Line_Mes.clear()
		if self.Line_Mes.hasAcceptableInput() and \
		self.Line_Ano.hasAcceptableInput():
			self.frame_2.setEnabled(True)
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
		self.B_Mod.setEnabled(True)
		self.B_Anular.setEnabled(True)
		self.G_Fact.setEnabled(True)
		self.G_Cliente.setEnabled(True)
		self.G_Dfact.setEnabled(True)
		self.L_Comp.setEnabled(False)
		self.B_Agregar.setEnabled(False)
		self.B_Elim.setEnabled(True)
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
		self.Line_Total.setText(locale.currency(float(row[10]),
			grouping=True, symbol=False))
		self.cuitT = row[3]

	##==============================================##
	def ModFact(self):
		''' Se prepara la UI para la modificacion de una factura '''
		self.BandMod = True
		self.B_Mod.setEnabled(False)
		self.B_Elim.setEnabled(False)
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
				DBL.Execute(Query)
				
				Query = "DELETE FROM venta_productos WHERE N_fact LIKE '%s'" % self.L_Fact.text()
				DBL.Execute(Query)

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

class Busc_CliV(QWidget, Ui_B_Clientes):
	''' MDI de busqueda de clintes '''

	def __init__(self, parent):
		super(Busc_CliV, self).__init__()
		self.setupUi(self)
		self.setWindowIcon(QIcon(ico_dir + "\\Icon.ico"))
		#Se guarda en una variable el widget del padre para poder enviarle información. 
		#Digamos que es un puntero, este razonamiento se utliza en todos los casos.
		self.padre = parent
		self.Tabla_Clientes.installEventFilter(self)

	##==============================================##
	def Cerrar(self):
		self.close()

	def closeEvent(self, event):
		self.padre.BCliente = False

	##==============================================##
	def eventFilter(self, target, event):
		if target is self.Tabla_Clientes and event.type() == QEvent.KeyPress:
			if event.key() == Qt.Key_Return:
				try:
					self.Resultados(self.Tabla_Clientes.currentRow(),
						self.Tabla_Clientes.currentColumn())
				except:
					pass
		return False

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


class Clientes(QWidget, Ui_ABMCli):
	''' MDI que instancia el ABM de Clientes, mantiene el formato de
	Proveedores '''
	def __init__(self):
		super(Clientes, self).__init__()
		self.setupUi(self)
		self.setWindowIcon(QIcon(ico_dir + "\\Icon.ico"))
		self.B_Search.setIcon(QIcon(ico_dir + "\\Search.png"))
		self.Inicializar()
		int_2 = QRegExpValidator(QRegExp("([0-9]{2})[-]([0-9]{8})[-]([0-9]{1})"))
		self.Line_Cuit.setValidator(int_2)
		self.BCliente = False
		self.B_Search.setEnabled(False)
		self.groupBox_2.setEnabled(False)

	##==============================================##
	def closeEvent(self, event):
		main.ClienOpen = False
		try:
			main.MDI.setActiveSubWindow(self.BCliente)
			main.MDI.closeActiveSubWindow()
		except:
			pass
	
	def Cerrar(self):
		VentanaPrincipal.Cerrar(self)

	##==============================================##
	def Inicializar(self):
		self.Line_Cuit.setFocus()
		rowsZ = DBL.Queryall("SELECT Nombre FROM zonas")
		rowsL = DBL.Queryall("SELECT Nombre FROM listas")
		rowsI = DBL.Queryall("SELECT Descripcion FROM resp_iva")
		for row in rowsZ:
			self.Box_Prov.addItem(str(row[0]))
			if self.Box_Prov.findText('CHACO') == -1:
				self.Box_Prov.setCurrentIndex(0)
			else:
				self.Box_Prov.setCurrentIndex(self.Box_Prov.findText('CHACO'))
		for row in rowsL:
			self.Box_Lista.addItem(str(row[0]))
			if self.Box_Lista.findText('MOSTRADOR') == -1:
				self.Box_Lista.setCurrentIndex(0)
			else:
				self.Box_Lista.setCurrentIndex(self.Box_Lista.findText('MOSTRADOR'))
		for row in rowsI:
			self.Box_Resp.addItem(str(row[0]))
			if self.Box_Resp.findText('RESPONSABLE INSCRIPTO') == -1:
				self.Box_Resp.setCurrentIndex(0)
			else:
				self.Box_Resp.setCurrentIndex(self.Box_Resp.findText('RESPONSABLE INSCRIPTO'))

	##==============================================##
	def Validacion(self):
		if self.Line_Cuit.hasAcceptableInput() \
		and (self.Line_RazonS.text()
		and self.Line_Direc.text()) not in ['', ' ']:
			if (self.Line_RazonS.text().find('\'') == -1 and 
				self.Line_Direc.text().find('\'') == -1 and 
				self.Line_Alias.text().find('\'') == -1):
				return True
		else:
			return False

	##==============================================##
	def B_Clientes(self):
		""" Abre la ventana de buscar Clientes """
		if not self.BCliente:
			self.BCliente = main.AbrirMDI(B_ClientesC(main.MDI.activeSubWindow().widget()))
		else:
			main.MDI.setActiveSubWindow(self.BCliente)

	##==============================================##
	def AMCliente(self):
		""" Alta y Modificacion de Clientes """
		if self.Validacion():
			Cuit = self.Line_Cuit.text()
			RazonS = self.Line_RazonS.text().upper().replace(',', '')
			Direc = self.Line_Direc.text().upper()
			Prov = self.Box_Prov.currentText()
			Resp = self.Box_Resp.currentText()
			List = self.Box_Lista.currentText()
			Alias = self.Line_Alias.text().upper()

			try:
				if self.B_Agregar.text() == 'Agregar':
					Query = "INSERT INTO clientes (Cuit, RazonS, Direccion, Provincia, Alias,Lista, Responsabilidad) \
						VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (Cuit, RazonS, Direc, Prov, Alias, List, Resp)
					DBL.Execute(Query)
		
					main.statusBar.showMessage("Guardado exitoso", 5000)
					main.statusBar.setStyleSheet("color: rgb(0, 85, 0)")
				else:
					Query = "UPDATE clientes SET Cuit = '%s', RazonS = '%s', \
						Direccion = '%s', Provincia = '%s', Alias = '%s', Lista = '%s', \
						Responsabilidad = '%s' WHERE Cuit LIKE '%s'" % (Cuit, RazonS, Direc, Prov, 
							Alias, List, Resp, Cuit)
					DBL.Execute(Query)

					if self.Check_Cam.isChecked():
						Desc = str(self.Line_Desc.value())
						Rec = str(self.Line_Rec.value())
						chk = '0'
						List2 = self.Box_ListaC.currentText()

						if self.Check_Cam2.isChecked():
							chk = '1'

						try:
							Query = "INSERT INTO %s.clientes (Cuit, RazonS, Direccion, Provincia, Alias,Lista, \
								Responsabilidad, Descuento, Recargo, Duplicado) \
								VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (config['CAMIONETA']['DB_NAME'], Cuit, 
								RazonS, Direc, Prov, Alias, List2, Resp, Desc, Rec, chk)
							DBL.Execute(Query)
						except:
							Query = "UPDATE %s.clientes SET Cuit = '%s', RazonS = '%s', \
								Direccion = '%s', Provincia = '%s', Alias = '%s', Lista = '%s', \
								Responsabilidad = '%s', Descuento = '%s', Recargo = '%s', Duplicado = '%s' WHERE Cuit \
								LIKE '%s'" % (config['CAMIONETA']['DB_NAME'], Cuit, RazonS, Direc, Prov, Alias,
									List2, Resp, Desc, Rec, chk, Cuit)
							DBL.Execute(Query)
					else:
						try:
							Query = "DELETE FROM %s.clientes WHERE Cuit = '%s'" % (config['CAMIONETA']['DB_NAME'], Cuit)
							DBL.Execute(Query)
						except:
							pass
					main.statusBar.showMessage("Modificacion exitosa", 5000)
					main.statusBar.setStyleSheet("color: rgb(0, 85, 0)")
				self.Clear()
			except mysql.connector.IntegrityError:
				main.statusBar.showMessage("Error, cliente duplicado", 5000)
				main.statusBar.setStyleSheet("color: rgb(170, 0, 0)")
				VentanaPrincipal.CrearLogs(self)
		else:
			main.statusBar.showMessage("Faltan datos, o datos erroneos", 5000)
			main.statusBar.setStyleSheet("color: rgb(170, 0, 0)")

	##==============================================##
	def ECliente(self):
		""" Eliminacion de Clientes """
		""" Si hay Clientes con boletas no se podra eliminar el Cliente """
		try:
			Cod = self.Line_Cuit.text()
			Query = "DELETE FROM clientes WHERE Cuit = '%s'" % Cod
			DBL.Execute(Query)

			self.Clear()
			main.statusBar.showMessage("Eliminacion Exitosa", 5000)
			main.statusBar.setStyleSheet("color: rgb(0, 85, 0)")
		except mysql.connector.IntegrityError:
			main.statusBar.showMessage("Accion Denegada", 5000)
			main.statusBar.setStyleSheet("color: rgb(170, 0, 0)")
			VentanaPrincipal.CrearLogs(self)
	
	##==============================================##
	def Clear(self):
		self.Line_Cuit.clear()
		self.Line_RazonS.clear()
		self.Line_Direc.clear()
		self.Line_Alias.clear()
		self.Box_Prov.setCurrentIndex(self.Box_Prov.findText('CHACO'))
		self.Box_Lista.setCurrentIndex(self.Box_Lista.findText('MOSTRADOR'))
		self.Box_Resp.setCurrentIndex(self.Box_Resp.findText('RESPONSABLE INSCRIPTO'))
		self.Line_Desc.setValue(0.00)
		self.Line_Rec.setValue(0.00)
		self.Check_Cam.setChecked(False)
		self.Check_Cam2.setChecked(False)
		self.B_Eliminar.setEnabled(False)
		self.B_Agregar.setText('Agregar')
		self.B_Agregar.setEnabled(True)
		self.B_Buscar.setEnabled(True)
		self.B_Search.setEnabled(True)
		self.Line_Cuit.setEnabled(True)
		self.Line_Cuit.setFocus()

class B_ClientesC(QWidget, Ui_B_Clientes):
	def __init__(self, padre):
		super(B_ClientesC, self).__init__()
		self.setupUi(self)
		self.setWindowIcon(QIcon(ico_dir + "\\Icon.ico"))
		self.Win = padre
		self.Win.L_Coment.clear()

	##==============================================##
	def closeEvent(self, event):
		self.Win.BCliente = False
		try:
			main.MDI.setActiveSubWindow(main.ClienOpen)
		except:
			pass
		
	def Cerrar(self):
		VentanaPrincipal.Cerrar(self)	
	##==============================================##
	def QueryClientes(self):
		self.Tabla_Clientes.setRowCount(0)
		self.Tabla_Clientes.setColumnCount(2)
		self.Tabla_Clientes.setHorizontalHeaderLabels(['Razón Social', 'Alias'])
		self.Tabla_Clientes.horizontalHeader().setStretchLastSection(True)
		self.Tabla_Clientes.setColumnWidth(0, 340)
		i = 0
		Name = self.Line_Cliente.text()

		if self.R_Razon.isChecked():
			Query = "SELECT RazonS, Alias FROM clientes WHERE RazonS LIKE \
				concat('%%','%s','%%')" % Name
		elif self.R_Cuit.isChecked():
			Query = "SELECT RazonS, Alias FROM clientes WHERE Cuit LIKE \
				concat('%%','%s','%%')" % Name
		elif self.R_Alias.isChecked():
			Query = "SELECT RazonS, Alias FROM clientes WHERE Alias LIKE \
				concat('%%','%s','%%')" % Name
		rows = DBL.Queryall(Query)

		for row in rows:
			self.Tabla_Clientes.insertRow(i)
			self.Tabla_Clientes.setItem(i, 0, main.CrearItem(str(row[0]), 10, 'RS'))
			self.Tabla_Clientes.setItem(i, 1, main.CrearItem(str(row[1]), 10, 'RS'))
			i = + 1
		self.Tabla_Clientes.resizeRowsToContents()
		self.Tabla_Clientes.sortItems(0, order=Qt.AscendingOrder)

	##==============================================##
	def Resultados(self, row=-1, column=None):
		if row >= 0:
			Name = self.Tabla_Clientes.item(row, 0).text()
			Query = "SELECT * FROM clientes WHERE RazonS LIKE '%s'" % Name
		else:
			Query = "SELECT * FROM clientes WHERE Cuit LIKE '%s'" % (
				self.Win.Line_Cuit.text())
		rows = DBL.Queryone(Query)

		if rows:
			self.Win.Line_Cuit.setText(rows[0])
			self.Win.Line_RazonS.setText(rows[1])
			self.Win.Line_Direc.setText(rows[2])
			self.Win.Box_Prov.setCurrentIndex(self.Win.Box_Prov.findText(rows[3]))
			self.Win.Line_Alias.setText(rows[4])
			self.Win.Box_Lista.setCurrentIndex(self.Win.Box_Lista.findText(rows[5]))
			self.Win.Box_Resp.setCurrentIndex(self.Win.Box_Resp.findText(rows[6]))
			self.Win.L_Coment.clear()
			self.Win.B_Agregar.setText('Modificar')
			self.Win.B_Eliminar.setEnabled(True)
			self.Win.B_Buscar.setEnabled(False)
			self.Win.B_Search.setEnabled(False)

			Query = "SELECT Descuento, Recargo, Lista, Duplicado FROM %s.clientes \
				WHERE Cuit LIKE '%s'" % (config['CAMIONETA']['DB_NAME'], rows[0])
			rowx = DBL.Queryone(Query)

			if rowx:
				self.Win.Line_Desc.setValue(float(rowx[0]))
				self.Win.Line_Rec.setValue(float(rowx[1]))
				self.Win.Box_ListaC.setCurrentIndex(self.Win.Box_ListaC.findText(rowx[2]))
				self.Win.Check_Cam.setChecked(True)
				if rowx[3] == '1':
					self.Win.Check_Cam2.setChecked(True)
			if row >= 0:
				main.MDI.activeSubWindow().close()
				main.MDI.activatePreviousSubWindow()
			return True
		else:
			return False

	##==============================================##
	def setFocus(self):
		self.Line_Cliente.setFocus()
		self.QueryClientes()




class Precios(QWidget, Ui_Precios):
	""" Clase que administra los precios de los productos segun una lista """
	def __init__(self):
		super(Precios, self).__init__()
		self.setupUi(self)
		self.setWindowIcon(QIcon(ico_dir + "\\Icon.ico"))
		self.Inicializar()
		self.installEventFilter(self)
		self.R_Camio.setEnabled(False)
	
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
				Query = "UPDATE productos SET Precio = '%s', Fecha = '%s' \
					WHERE Lista = '%s' AND Nombre = '%s' " % ('{:.4f}'.format(float(item.text())), date.today(), Lista, Nombre)
				DBL.Execute(Query)
				item.tableWidget().item(item.row(), 1).setText('{:.4f}'.format(float(item.text())))
				item.tableWidget().item(item.row(), 2).setText(Fecha)
			except:
				VentanaPrincipal.showAlerta(self, 1, 'Valor invalido')
				item.tableWidget().item(item.row(), 1).setText(self.Precio)
			self.T_Lista.blockSignals(False)
	
	##==============================================##
	def Search(self, texto = ''):
		self.T_Lista.setRowCount(0)
		Query = "SELECT Nombre, Precio, Fecha FROM productos WHERE \
				Lista = '%s' AND Nombre LIKE '%%%s%%'" % (self.Lista, texto)
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
		rows = DBL.Queryall("SELECT * FROM listas")
		for row in rows:
			self.C_Lista.addItem(str(row[1]))


class SplashScreen(QWidget, Ui_Splash):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.setWindowFlag(Qt.FramelessWindowHint)
		icon = QIcon()
		icon.addPixmap(QPixmap(ico_dir + "\\Icon.ico"), QIcon.Normal, QIcon.Off)
		self.setWindowIcon(icon)
		
		self.counter = 0
		self.n = 80 # total instance

		self.progressBar.setRange(0, self.n)

		self.timer = QTimer()
		self.timer.timeout.connect(self.loading)
		self.timer.start(30)

	def loading(self):
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

		self.counter += 2




""" Unicamente disponible las funciones Ventas, Clientes y Precios (que se encuentra en la pestaña Productos) """


""" Ejecucion del programa 
	- Se crea un archivo .lock que no se borra hasta 
		que no se cierra el programa
	- Si el archivo está creado, no se podrá abrir otra instancia del programa,
		por lo tanto se llamará al except. Donde se notifica.
	- Se cuenta con un directorio temporal para algunas cosas del programa,
		para no "ensuciar" la carpeta raiz. """

app = QApplication(sys.argv)

temp_base = Path(tempfile.gettempdir())
cache_dir = temp_base / "Gestor_cache"
cache_dir.mkdir(exist_ok=True)
lock = FileLock(cache_dir / "Gestor.lock")
ico_dir = resource_path("Iconos")

aux = resource_path('Iconos\\Arrow-Down.png').replace("\\", "/")
with fileinput.FileInput(resource_path("Aqua.qss"), 
		inplace=True, backup='.bak') as file:
    for line in file:
       print(line.replace('downarrowcbox', aux), end='')


try:
	with lock.acquire(timeout=2):
		config = configparser.ConfigParser()
		config.read(os.path.expanduser('~\\config.ini'))
		locale.setlocale(locale.LC_ALL, '')
		
		file = open(resource_path("Aqua.qss"), 'r')
		with file:
			qss = file.read()
			app.setStyleSheet(qss)
		
		main = VentanaPrincipal()
		main.statusBar.setFont(QFont('Yu Gothic', 10, QFont.Bold)) #Formateo la letra del StatusBar
		DBL = DbLocal() #Se instancia BD
		
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