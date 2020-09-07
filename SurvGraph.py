from PyQt5 import QtCore, QtGui, QtWidgets
from tempfile import gettempdir
from scipy.interpolate import interp1d
from numpy import linspace, real, fft, abs, sort
import pyqtgraph as pg
import file_buttons
import matplotlib.pyplot as plt
from os.path import join
from matplotlib.patches import Patch


class Ui_MainWindow(object):

    # Desabilita os botões
    def clearlines(self):
        self.line_Pontos.clear()
        self.line_ValorFinal.clear()
        self.line_ValorInicial.clear()

    # Função para escrever os dados do gráfico
    def writecoordfiles(self, x_esc, y_esc, name):
        with open(name, "w") as writecoord:

            tipo = name[-3::].lower()

            if tipo == "txt":
                writecoord.write("X    Y \n")

                for i in range(0, len(x_esc)):
                    writecoord.write(
                        str(x_esc[i]) + "    " + str(y_esc[i]) + "\n")
                    i += 1
            elif tipo == "csv":
                writecoord.write("X;Y \n")

                for i in range(0, len(x_esc)):
                    writecoord.write(
                        str(x_esc[i]) + ";" + str(y_esc[i]) + "\n")
                    i += 1

    # Função para ler os dados do gráfico
    def readcoordfiles(self, name, tip):
        with open(name, "r") as readcoord:
            x_ent = []
            y_ent = []

            tipo = name[-3::].lower()

            # Pega os dados de um .txt e formata para o padrão .py
            if tipo == "txt":
                for linha in readcoord:
                    try:
                        if tip == "complex":
                            y_ent.append(
                                complex(linha.split()[1].replace(",", ".")))
                        else:
                            y_ent.append(
                                float(linha.split()[1].replace(",", ".")))

                        x_ent.append(float(linha.split()[0].replace(",", ".")))
                    except ValueError:
                        pass
                    except IndexError:
                        pass

            # Pega os dados de um .csv e formata para o padrão .py
            elif tipo == "csv":
                for linha in readcoord:
                    try:
                        if tip == "complex":
                            y_ent.append(
                                complex(linha.split(";")[1].replace(",", ".")))
                        else:
                            y_ent.append(
                                float(linha.split(";")[1].replace(",", ".")))

                        x_ent.append(
                            float(linha.split(";")[0].replace(",", ".")))
                    except ValueError:
                        pass
                    except IndexError:
                        pass

        return x_ent, y_ent

    # Função para plotar o gráfico
    def plotGraphic(self, x_plot, y_plot):
        self.graphicsView.clear()
        self.graphicsView.plot(x_plot, y_plot)
        self.graphicsView.showGrid(x=True, y=True)
        self.graphicsView.enableAutoRange(x=True, y=True)
        self.graphicsView.setLabel(
            "left", text="Eixo Y",
        )
        self.graphicsView.setLabel("bottom", text="Eixo X")

    # Função para plotar gráfico de barra
    def plotGraphicbar(self, x_plot, y_plot):
        try:
            self.graphicsView.clear()
            bar = pg.BarGraphItem(x=x_plot, height=y_plot,
                                  width=0.01)

            self.graphicsView.addItem(bar)
            self.graphicsView.enableAutoRange(x=True, y=True)

            if self.label_pg.text() == "4":
                self.graphicsView.setTitle("Transformada de Fourier")
                self.graphicsView.setLabel("left", text="Amplitude")
                self.graphicsView.setLabel("bottom", text="Frequência (Hz)")
            else:
                self.graphicsView.setTitle(None)
                self.graphicsView.setLabel("left", text="Eixo Y")
                self.graphicsView.setLabel("bottom", text="Eixo X")

            return True

        except ValueError:
            self.label_erro.setText("Arquivo inválido")
            return False

    # Função que faz interpolação dos pontos do gráfico
    def intepolação(self, x_ant, y_ant, m):
        X = sort(x_ant)  # Converte o x_ent(list) em um array

        # Cria valores de x espado uniformemente
        x_plot = linspace(X.min(), X.max(), m)

        # Interpola novos valores de y para as coordenadas x uniformizadas

        if self.radioButton.isChecked():
            # interpolação linear
            interp = interp1d(x_ant, y_ant, kind='linear')
        elif self.radioButton_2.isChecked():
            # Interpolação Quadratica
            interp = interp1d(x_ant, y_ant, kind='quadratic')
        elif self.radioButton_3.isChecked():
            # Interpolação cubica
            interp = interp1d(x_ant, y_ant, kind='cubic')

        y_plot = interp(x_plot)
        return x_plot, y_plot

    # Funções do botão open
    def buttonOpen(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            None, "", "", "Arquivos de texto (*.txt);; Arquivos do Excel (*.csv) "
        )

        if filename[0]:

            coord = self.readcoordfiles(str(filename[0]), None)

            if not coord[0]:
                self.label_erro.setText("Arquivo inválido")
            else:
                self.radioButton.setChecked(True)

                n = len(coord[0])
                coord_unif = self.intepolação(coord[0], coord[1], n)

                self.writecoordfiles(
                    coord_unif[0], coord_unif[1], join(
                        gettempdir(), "__graficobackup.txt"))

                self.writecoordfiles(coord_unif[0], coord_unif[1], join(
                    gettempdir(), "__oldgrafico.txt"))

                self.writecoordfiles(coord_unif[0], coord_unif[1], join(
                    gettempdir(), "__newgrafico.txt"))

                self.clearlines()
                self.line_Pontos.setText(str(n))
                self.label_pg.setText("1")
                self.exibicao()
                self.groupBox.show()
                self.Button_save.setEnabled(True)
                self.Button_Export.setEnabled(True)
                self.plotGraphic(coord_unif[0], coord_unif[1])

                self.label_erro.setText(
                    "Use o menu no topo para recortar um intervalo do gráfico ou alterar a quantidade de pontos"
                )

    # Funções do botão ok - faz os espaçamento uniforme da coordenada x
    def buttonOk(self):
        try:
            n = int(self.line_Pontos.text())
            coord = self.readcoordfiles(join(
                gettempdir(), "__oldgrafico.txt"), None)
            coord_new = self.intepolação(coord[0], coord[1], n)
            self.writecoordfiles(
                coord_new[0], coord_new[1], join(
                    gettempdir(), "__newgrafico.txt"))
            self.plotGraphic(coord_new[0], coord_new[1])

            if self.label_pg.text() != "3":
                self.label_pg.setText("1")
            self.exibicao()
            self.label_erro.setText(
                "Mudança de pontos realizado com sucesso!"
            )
        except ValueError:
            self.label_erro.setText("Digite apenas valores inteiros")
            self.clearlines()

    # Funções para resetar os pontos ao inicial
    def resetarpontos(self):
        coord_new = self.readcoordfiles(join(
            gettempdir(), "__oldgrafico.txt"), None)
        self.writecoordfiles(
            coord_new[0], coord_new[1], join(gettempdir(), "__newgrafico.txt")
        )

        self.plotGraphic(coord_new[0], coord_new[1])
        self.line_Pontos.setText(str(len(coord_new[0])))

        if self.label_pg.text() != "3":
            self.label_pg.setText("1")
        self.exibicao()
        self.label_erro.setText("Pontos resetados!")

    # Função mostra a fft do grafico com os harmonicos deletados
    def buttonsuavizargrafico(self):
        try:

            coord = self.readcoordfiles(join(
                gettempdir(), "__newgrafico.txt"), None)

            Y = fft.fft(coord[1])  # Transformada rápida de fourier
            m = len(Y)

            # Plotagem do gráfico com os harmônicos
            X = linspace(0, m - 1, m)
            X_plot = linspace(0, m/2, m//2)
            self.label_pg.setText("2")
            self.plotGraphicbar(X_plot, Y)

            self.writecoordfiles(X, Y, join(
                gettempdir(), "__newharmonicos.txt"))
            self.writecoordfiles(X, Y, join(
                gettempdir(), "__oldharmonicos.txt"))

            self.exibicao()

        except ValueError:
            self.label_erro.setText("Dados de entrada inválidos")
            self.clearlines()

    # Deleta os Harmônicos
    def delhamonicos(self):

        try:

            if self.label_pg.text() == "2":
                inicial = int(self.line_ValorInicial.text().strip())
                final = int(self.line_ValorFinal.text().strip())

                coord = self.readcoordfiles(join(
                    gettempdir(), "__newharmonicos.txt"), "complex")
                y = coord[1]
                m = len(y)

                if final > m/2:
                    final = m//2
                if inicial < 1:
                    inicial = 1
                i = 0
                for i in range(inicial - 1, final):
                    y[i+1] = 0
                    y[m-1-i] = 0

                x_plot = linspace(0, m/2, m//2)
                self.plotGraphicbar(x_plot, y)
                self.writecoordfiles(
                    coord[0], y, join(gettempdir(), "__newharmonicos.txt"))
                self.comparagráficos("print")
                self.line_Pontos.setText(str(m))
                self.label_erro.setText(
                    "Harmônicos deletados com sucesso!")

            elif self.label_pg.text() == "4":
                self.delIntervalo("__newfft.txt")
            else:
                self.delIntervalo("__newgrafico.txt")

        except ValueError:
            self.label_erro.setText("Digite somente valores inteiros")

    # recorta intervalos do gráfico
    def delIntervalo(self, newname):
        inicial = float(
            self.line_ValorInicial.text().replace(",", ".").strip())
        final = float(
            self.line_ValorFinal.text().replace(",", ".").strip())

        if final < inicial:
            self.label_erro.setText("Valor fora do intervalo!")
        else:

            coord = self.readcoordfiles(join(
                gettempdir(), newname), None)
            x = coord[0]

            y = coord[1]
            i = 0

            if inicial < x[0]:
                inicial = x[0]

            while(x[0] < inicial):
                del x[0]
                del y[0]

            v = len(x)

            if final > x[v-1]:
                i = v
            else:
                while(x[i] <= final):
                    i += 1

            for k in range(i, v):
                del y[i]
                del x[i]

            self.writecoordfiles(x, y, join(gettempdir(), newname))

            if self.label_pg.text() != "4":
                self.writecoordfiles(
                    x, y, join(gettempdir(), "__oldgrafico.txt"))
                self.plotGraphic(x, y)
                self.line_Pontos.setText(str(len(x)))
            else:
                self.plotGraphicbar(x, y)
        self.label_erro.setText("Intervalo recortado com sucesso")

    # reseta os Harmônicos excluidos
    def resetHarmonicos(self):
        if self.label_pg.text() == "2":
            oldcoord = self.readcoordfiles(
                join(gettempdir(), "__oldharmonicos.txt"), "complex")
            m = len(oldcoord[0])
            x_plot = linspace(0, m/2, m//2)
            self.plotGraphicbar(x_plot, oldcoord[1])
            self.writecoordfiles(
                oldcoord[0], oldcoord[1], join(
                    gettempdir(), "__newharmonicos.txt")
            )
            self.comparagráficos(None)
            self.line_Pontos.setText(str(m))
            self.label_erro.setText("Harmônicos resetados!")
        elif self.label_pg.text() == "4":
            oldcoord = self.readcoordfiles(join(
                gettempdir(), "__oldfft.txt", None))

            self.plotGraphicbar(oldcoord[0], oldcoord[1])
            self.writecoordfiles(
                oldcoord[0], oldcoord[1], join(gettempdir(), "__newfft.txt")
            )
            self.line_Pontos.setText(str(len(oldcoord[0])))
            self.label_erro.setText("Gráfico resetado!")

        else:
            oldcoord = self.readcoordfiles(join(
                gettempdir(), "__graficobackup.txt"), None)

            self.plotGraphic(oldcoord[0], oldcoord[1])
            self.writecoordfiles(
                oldcoord[0], oldcoord[1], join(
                    gettempdir(), "__newgrafico.txt")
            )
            self.writecoordfiles(
                oldcoord[0], oldcoord[1], join(
                    gettempdir(), "__oldgrafico.txt")
            )
            self.line_Pontos.setText(str(len(oldcoord[0])))
            self.label_erro.setText("Gráfico resetado!")

    # Plota uma comparação dos gráficos
    def comparagráficos(self, comp):

        fft_coord = self.readcoordfiles(join(
            gettempdir(), "__newharmonicos.txt"), "complex")
        coord = self.readcoordfiles(
            join(gettempdir(), "__newgrafico.txt"), None)

        # transformada inversa (parte real)
        y_ifft = real(fft.ifft(fft_coord[1]))

        plot_coord = self.intepolação(coord[0], y_ifft, len(coord[0]))
        self.writecoordfiles(
            coord[0], y_ifft, join(gettempdir(), "__newgrafico.txt"))

        if comp == "print":
            oldcoord = self.readcoordfiles(join(
                gettempdir(), "__oldgrafico.txt"), None)
            plt.close()
            plt.figure("Comparação dos gráfico")
            plt.title("Comparação dos gráfico")
            old = Patch(color="gray", label="Gráfico antigo")
            new = Patch(color="blue", label="Gráfico novo")
            plt.legend(handles=[old, new])
            plt.xlabel("Eixo X")
            plt.ylabel("Eixo Y")
            plt.plot(oldcoord[0], oldcoord[1], color="gray")
            plt.plot(plot_coord[0], plot_coord[1], color="blue")
            plt.show()

    # Plota o gráfico final
    def buttonseguir(self):

        plot_coord = self.readcoordfiles(join(
            gettempdir(), "__newgrafico.txt"), None)
        self.plotGraphic(plot_coord[0], plot_coord[1])
        self.writecoordfiles(
            plot_coord[0], plot_coord[1], join(
                gettempdir(), "__oldgrafico.txt")
        )
        self.writecoordfiles(
            plot_coord[0], plot_coord[1], join(gettempdir(), "__graficobackup.txt"))
        self.label_pg.setText("3")
        self.exibicao()
        m = len(plot_coord[0])
        self.line_Pontos.setText(str(m))
        self.label_erro.setText(
            "Use o menu no topo para recortar um intervalo do gráfico ou alterar a quantidade de pontos")

    # Volta para o gráfico de harmonicos
    def buttonBack(self):
        coord = self.readcoordfiles(join(
            gettempdir(), "__newharmonicos.txt"), "complex")
        m = len(coord[0])
        X_plot = linspace(1, m/2, m//2)
        self.plotGraphicbar(X_plot, coord[1])
        self.label_pg.setText("2")
        self.exibicao()

    # Salva as imagens do gráfico no caminho escolhido
    def salvarImagem(self):

        GrafWindow.show()
        ui_graf.novafigura()

    #  Define os padrões para salvar o gráfico
    def caminhoparasalvargrafico(self):
        pg = self.label_pg.text()

        if pg == "1" or pg == "3":
            dados = "__newgrafico.txt"
            tipo = None
            graf = "plot"

        elif pg == "2":
            dados = "__newharmonicos.txt"
            tipo = "complex"
            graf = "bar"

        elif pg == "4":
            dados = "__newfft.txt"
            tipo = None
            graf = "bar"

        coord = self.readcoordfiles(join(gettempdir(), dados), tipo)

        return coord, graf

    # Exporta os dados do gráfico
    def exportarDadosgrafico(self):

        ExportWindow.show()

    # Realiza a transformada de fourier
    def fft(self):
        try:

            coord = self.readcoordfiles(join(
                gettempdir(), "__newgrafico.txt"), None)

            N = len(coord[1])
            self.line_Pontos.setText(str(N))

            # aplica a FFT
            yfft = fft.fft(coord[1])
            X = coord[0]
            T = X[2]-X[1]
            xfft = linspace(0.0, 1.0 / (2.0 * T), N // 2)

            y_plot = 2.0 / N * abs(yfft[: N // 2])

            self.label_pg.setText("4")
            self.plotGraphicbar(xfft, y_plot)

            self.writecoordfiles(xfft, y_plot, join(
                gettempdir(), "__newfft.txt"))
            self.writecoordfiles(xfft, y_plot, join(
                gettempdir(), "__oldfft.txt"))

            self.exibicao()

            self.label_erro.setText(
                "Transformada de Fourier realizada com sucesso! Dica- Recorte o gráfico para melhorar a visualização")

        except ValueError:
            self.label_erro.setText("Digite apenas valores reais")
            self.clearlines()

    # Defina os objetos a serem exibidos em cada ação
    def exibicao(self):
        pg = self.label_pg.text()

        self.line_ValorInicial.setText("")
        self.line_ValorFinal.setText("")
        if pg == "0":
            self.groupBox_2.hide()
            self.groupBox.hide()
            self.frame_SeguirBack.hide()
            self.Button_save.setEnabled(False)
            self.Button_Export.setEnabled(False)
            self.Button_Fft.setEnabled(False)
            self.Button_Suavizar.setEnabled(False)

        elif pg == "1":
            self.frame_SeguirBack.hide()
            self.groupBox_2.show()
            self.Button_Suavizar.setEnabled(True)
            self.Button_Fft.setEnabled(True)
            self.groupBox_2.setTitle("Recortar")

        elif pg == "2":
            self.frame_SeguirBack.show()
            self.Button_back.hide()
            self.Button_Ok.show()
            self.Button_Fft.setEnabled(False)
            self.Button_Suavizar.setEnabled(False)
            self.label_erro.setText(
                "Delete o(s) intervalo(s) que tenha(m) os menores harmônicos para retirar os ruídos do gráfico"
            )
            self.groupBox_2.setTitle("Deletar")
        elif pg == "3":
            self.Button_back.show()
            self.Button_Ok.hide()
            self.Button_Fft.setEnabled(True)
            self.Button_Suavizar.setEnabled(False)
            self.groupBox_2.setTitle("Recortar")
        elif pg == "4":
            self.frame_SeguirBack.hide()
            self.Button_Fft.setEnabled(False)
            self.Button_Suavizar.setEnabled(True)
            self.groupBox_2.setTitle("Recortar")

    # Exibe a tela sobre do programa
    def sobre(self):
        SobreWindow.show()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(950, 590)
        MainWindow.setMinimumSize(QtCore.QSize(950, 590))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Buttons/Buttons/ico.ico"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.menu_top = QtWidgets.QFrame(self.centralwidget)
        self.menu_top.setMinimumSize(QtCore.QSize(0, 70))
        self.menu_top.setMaximumSize(QtCore.QSize(16777215, 70))
        self.menu_top.setStyleSheet("")
        self.menu_top.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.menu_top.setFrameShadow(QtWidgets.QFrame.Raised)
        self.menu_top.setObjectName("menu_top")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.menu_top)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frame = QtWidgets.QFrame(self.menu_top)
        self.frame.setMinimumSize(QtCore.QSize(50, 70))
        self.frame.setMaximumSize(QtCore.QSize(50, 70))
        self.frame.setStyleSheet("background-color: rgb(45, 45, 45);")
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.Button_Open = QtWidgets.QPushButton(self.frame)
        self.Button_Open.setGeometry(QtCore.QRect(0, 20, 50, 50))
        self.Button_Open.setStyleSheet("QPushButton{\n"
                                       "    Border-Radius:0px;\n"
                                       "}\n"
                                       "QPushButton:hover{\n"
                                       "    background-color: rgb(25, 25, 25);\n"
                                       "}\n"
                                       "QPushButton:pressed{\n"
                                       "    background-color: rgb(85, 85, 85);\n"
                                       "}")
        self.Button_Open.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(
            ":/Buttons/Buttons/Button_Open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_Open.setIcon(icon1)
        self.Button_Open.setIconSize(QtCore.QSize(40, 40))
        self.Button_Open.setAutoRepeat(False)
        self.Button_Open.setObjectName("Button_Open")
        self.horizontalLayout_2.addWidget(self.frame)
        self.frame_zoom = QtWidgets.QFrame(self.menu_top)
        self.frame_zoom.setMaximumSize(QtCore.QSize(16777215, 70))
        self.frame_zoom.setStyleSheet("background-color: rgb(60, 69, 85);")
        self.frame_zoom.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_zoom.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_zoom.setObjectName("frame_zoom")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_zoom)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame_4 = QtWidgets.QFrame(self.frame_zoom)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.groupBox = QtWidgets.QGroupBox(self.frame_4)
        self.groupBox.setGeometry(QtCore.QRect(380, 5, 311, 61))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setStyleSheet("color: rgb(255, 255, 255);")
        self.groupBox.setObjectName("groupBox")
        self.pushButton_Add_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_Add_2.setGeometry(QtCore.QRect(270, 15, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.pushButton_Add_2.setFont(font)
        self.pushButton_Add_2.setToolTip("")
        self.pushButton_Add_2.setStyleSheet("QPushButton{    \n"
                                            "    border:1px solid;\n"
                                            "    border-radius:10px;\n"
                                            "    border-color: rgb(255, 255, 255);\n"
                                            "    color: rgb(255, 255, 255);\n"
                                            "}\n"
                                            "QPushButton:hover{\n"
                                            "    background-color: rgb(100, 100, 100);\n"
                                            "}\n"
                                            "QPushButton:pressed{\n"
                                            "    background-color: rgb(85, 85, 85);\n"
                                            "}\n"
                                            "")
        self.pushButton_Add_2.setObjectName("pushButton_Add_2")
        self.label_quantidade = QtWidgets.QLabel(self.groupBox)
        self.label_quantidade.setGeometry(QtCore.QRect(20, 20, 151, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_quantidade.setFont(font)
        self.label_quantidade.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_quantidade.setObjectName("label_quantidade")
        self.line_Pontos = QtWidgets.QLineEdit(self.groupBox)
        self.line_Pontos.setGeometry(QtCore.QRect(180, 20, 80, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setKerning(True)
        self.line_Pontos.setFont(font)
        self.line_Pontos.setToolTip("")
        self.line_Pontos.setStyleSheet("QLineEdit{\n"
                                       "    borde:5px solid rgb(45,45,45);\n"
                                       "    border-radius: 6px;\n"
                                       "    background-color: rgb(30, 30, 30);\n"
                                       "    color: rgb(255, 255, 255);\n"
                                       "}\n"
                                       "QLineEdit:focus{\n"
                                       "    border:1px solid rgb(255, 255, 255);\n"
                                       "}")
        self.line_Pontos.setInputMethodHints(QtCore.Qt.ImhFormattedNumbersOnly)
        self.line_Pontos.setPlaceholderText("")
        self.line_Pontos.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.line_Pontos.setObjectName("line_Pontos")
        self.pushButton_restart_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_restart_2.setGeometry(QtCore.QRect(270, 37, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.pushButton_restart_2.setFont(font)
        self.pushButton_restart_2.setStyleSheet("QPushButton{\n"
                                                "    Border-Radius:0px;\n"
                                                "}\n"
                                                "QPushButton:hover{\n"
                                                "    \n"
                                                "    background-color: rgb(100, 100, 100);\n"
                                                "}\n"
                                                "QPushButton:pressed{\n"
                                                "    background-color: rgb(85, 85, 85);\n"
                                                "}\n"
                                                "")
        self.pushButton_restart_2.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(
            ":/Buttons/Buttons/Button_restart.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_restart_2.setIcon(icon2)
        self.pushButton_restart_2.setObjectName("pushButton_restart_2")
        self.radioButton = QtWidgets.QRadioButton(self.groupBox)
        self.radioButton.setGeometry(QtCore.QRect(30, 40, 41, 17))
        self.radioButton.setStyleSheet("color: rgb(255, 255, 255);")
        self.radioButton.setObjectName("radioButton")
        self.radioButton.setChecked(True)
        self.radioButton_2 = QtWidgets.QRadioButton(self.groupBox)
        self.radioButton_2.setGeometry(QtCore.QRect(80, 40, 31, 17))
        self.radioButton_2.setStyleSheet("color: rgb(255, 255, 255);")
        self.radioButton_2.setObjectName("radioButton_2")
        self.radioButton_3 = QtWidgets.QRadioButton(self.groupBox)
        self.radioButton_3.setGeometry(QtCore.QRect(130, 40, 41, 17))
        self.radioButton_3.setStyleSheet("color: rgb(255, 255, 255);")
        self.radioButton_3.setObjectName("radioButton_3")
        self.groupBox_2 = QtWidgets.QGroupBox(self.frame_4)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 5, 341, 61))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setStyleSheet("color: rgb(255, 255, 255);")
        self.groupBox_2.setObjectName("groupBox_2")
        self.line_ValorInicial = QtWidgets.QLineEdit(self.groupBox_2)
        self.line_ValorInicial.setGeometry(QtCore.QRect(106, 27, 80, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setKerning(True)
        self.line_ValorInicial.setFont(font)
        self.line_ValorInicial.setContextMenuPolicy(
            QtCore.Qt.DefaultContextMenu)
        self.line_ValorInicial.setToolTip("")
        self.line_ValorInicial.setStyleSheet("QLineEdit{\n"
                                             "    borde:5px solid rgb(45,45,45);\n"
                                             "    border-radius: 6px;\n"
                                             "    background-color: rgb(30, 30, 30);\n"
                                             "    color: rgb(255, 255, 255);\n"
                                             "}\n"
                                             "QLineEdit:focus{\n"
                                             "    border:1px solid rgb(255, 255, 255);\n"
                                             "}")
        self.line_ValorInicial.setInputMethodHints(
            QtCore.Qt.ImhFormattedNumbersOnly)
        self.line_ValorInicial.setPlaceholderText("")
        self.line_ValorInicial.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.line_ValorInicial.setObjectName("line_ValorInicial")
        self.pushButton_Add = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_Add.setGeometry(QtCore.QRect(310, 15, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.pushButton_Add.setFont(font)
        self.pushButton_Add.setStyleSheet("QPushButton{    \n"
                                          "    border:1px solid;\n"
                                          "    border-radius:10px;\n"
                                          "    border-color: rgb(255, 255, 255);\n"
                                          "    color: rgb(255, 255, 255);\n"
                                          "}\n"
                                          "QPushButton:hover{\n"
                                          "    background-color: rgb(100, 100, 100);\n"
                                          "}\n"
                                          "QPushButton:pressed{\n"
                                          "    background-color: rgb(85, 85, 85);\n"
                                          "}\n"
                                          "")
        self.pushButton_Add.setObjectName("pushButton_Add")
        self.label_inter = QtWidgets.QLabel(self.groupBox_2)
        self.label_inter.setGeometry(QtCore.QRect(10, 20, 91, 27))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_inter.setFont(font)
        self.label_inter.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_inter.setObjectName("label_inter")
        self.line_ValorFinal = QtWidgets.QLineEdit(self.groupBox_2)
        self.line_ValorFinal.setGeometry(QtCore.QRect(220, 27, 80, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setKerning(True)
        self.line_ValorFinal.setFont(font)
        self.line_ValorFinal.setToolTip("")
        self.line_ValorFinal.setStyleSheet("QLineEdit{\n"
                                           "    borde:5px solid rgb(45,45,45);\n"
                                           "    border-radius: 6px;\n"
                                           "    background-color: rgb(30, 30, 30);\n"
                                           "    color: rgb(255, 255, 255);\n"
                                           "}\n"
                                           "QLineEdit:focus{\n"
                                           "    border:1px solid rgb(255, 255, 255);\n"
                                           "}")
        self.line_ValorFinal.setInputMethodHints(
            QtCore.Qt.ImhFormattedNumbersOnly)
        self.line_ValorFinal.setPlaceholderText("")
        self.line_ValorFinal.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.line_ValorFinal.setObjectName("line_ValorFinal")
        self.pushButton_restart = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_restart.setGeometry(QtCore.QRect(310, 37, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.pushButton_restart.setFont(font)
        self.pushButton_restart.setStyleSheet("QPushButton{\n"
                                              "    Border-Radius:0px;\n"
                                              "}\n"
                                              "QPushButton:hover{\n"
                                              "    \n"
                                              "    background-color: rgb(100, 100, 100);\n"
                                              "}\n"
                                              "QPushButton:pressed{\n"
                                              "    background-color: rgb(85, 85, 85);\n"
                                              "}\n"
                                              "")
        self.pushButton_restart.setText("")
        self.pushButton_restart.setIcon(icon2)
        self.pushButton_restart.setObjectName("pushButton_restart")
        self.label_ate = QtWidgets.QLabel(self.groupBox_2)
        self.label_ate.setGeometry(QtCore.QRect(190, 27, 21, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setKerning(True)
        self.label_ate.setFont(font)
        self.label_ate.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_ate.setObjectName("label_ate")
        self.horizontalLayout_4.addWidget(self.frame_4)
        self.frame_logo = QtWidgets.QFrame(self.frame_zoom)
        self.frame_logo.setMinimumSize(QtCore.QSize(180, 0))
        self.frame_logo.setMaximumSize(QtCore.QSize(180, 16777215))
        self.frame_logo.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_logo.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_logo.setObjectName("frame_logo")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_logo)
        self.horizontalLayout_6.setContentsMargins(0, 5, 9, 4)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_logo = QtWidgets.QLabel(self.frame_logo)
        self.label_logo.setMinimumSize(QtCore.QSize(0, 40))
        self.label_logo.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_logo.setFont(font)
        self.label_logo.setStyleSheet("color: rgb(255, 255, 255);\n"
                                      "border:0px;")
        self.label_logo.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_logo.setText("")
        self.label_logo.setPixmap(QtGui.QPixmap(":/Buttons/Buttons/surv.png"))
        self.label_logo.setScaledContents(True)
        self.label_logo.setObjectName("label_logo")
        self.horizontalLayout_6.addWidget(self.label_logo)
        self.horizontalLayout_4.addWidget(self.frame_logo)
        self.horizontalLayout_2.addWidget(self.frame_zoom)
        self.frame_zoom.raise_()
        self.frame.raise_()
        self.verticalLayout.addWidget(self.menu_top)
        self.content = QtWidgets.QFrame(self.centralwidget)
        self.content.setStyleSheet("\n"
                                   "background-color: rgb(0, 0, 0);")
        self.content.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.content.setFrameShadow(QtWidgets.QFrame.Raised)
        self.content.setObjectName("content")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.content)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.menu_left = QtWidgets.QFrame(self.content)
        self.menu_left.setMinimumSize(QtCore.QSize(50, 0))
        self.menu_left.setMaximumSize(QtCore.QSize(50, 16777215))
        self.menu_left.setStyleSheet("background-color: rgb(45, 45, 45);")
        self.menu_left.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.menu_left.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.menu_left.setObjectName("menu_left")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.menu_left)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame_5 = QtWidgets.QFrame(self.menu_left)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.Button_Fft = QtWidgets.QPushButton(self.frame_5)
        self.Button_Fft.setGeometry(QtCore.QRect(0, 70, 50, 50))
        self.Button_Fft.setStyleSheet("QPushButton{\n"
                                      "    Border-Radius:0px;\n"
                                      "}\n"
                                      "QPushButton:hover{\n"
                                      "    background-color: rgb(25, 25, 25);\n"
                                      "}\n"
                                      "QPushButton:pressed{\n"
                                      "    background-color: rgb(85, 85, 85);\n"
                                      "}")
        self.Button_Fft.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(
            ":/Buttons/Buttons/Button_FFt.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_Fft.setIcon(icon3)
        self.Button_Fft.setIconSize(QtCore.QSize(40, 40))
        self.Button_Fft.setAutoRepeat(False)
        self.Button_Fft.setObjectName("Button_Fft")
        self.Button_Suavizar = QtWidgets.QPushButton(self.frame_5)
        self.Button_Suavizar.setGeometry(QtCore.QRect(0, 10, 50, 50))
        self.Button_Suavizar.setStyleSheet("QPushButton{\n"
                                           "    Border-Radius:0px;\n"
                                           "}\n"
                                           "QPushButton:hover{\n"
                                           "    background-color: rgb(25, 25, 25);\n"
                                           "}\n"
                                           "QPushButton:pressed{\n"
                                           "    background-color: rgb(85, 85, 85);\n"
                                           "}")
        self.Button_Suavizar.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(
            ":/Buttons/Buttons/Button_Graphic.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_Suavizar.setIcon(icon4)
        self.Button_Suavizar.setIconSize(QtCore.QSize(40, 40))
        self.Button_Suavizar.setAutoRepeat(False)
        self.Button_Suavizar.setObjectName("Button_Suavizar")
        self.Button_Sobre = QtWidgets.QPushButton(self.frame_5)
        self.Button_Sobre.setGeometry(QtCore.QRect(0, 130, 50, 50))
        self.Button_Sobre.setStyleSheet("QPushButton{\n"
                                        "    Border-Radius:0px;\n"
                                        "}\n"
                                        "QPushButton:hover{\n"
                                        "    background-color: rgb(25, 25, 25);\n"
                                        "}\n"
                                        "QPushButton:pressed{\n"
                                        "    background-color: rgb(85, 85, 85);\n"
                                        "}")
        self.Button_Sobre.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/Buttons/Buttons/sobre.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_Sobre.setIcon(icon5)
        self.Button_Sobre.setIconSize(QtCore.QSize(40, 40))
        self.Button_Sobre.setAutoRepeat(False)
        self.Button_Sobre.setObjectName("Button_Sobre")
        self.verticalLayout_3.addWidget(self.frame_5)
        self.frame_6 = QtWidgets.QFrame(self.menu_left)
        self.frame_6.setMaximumSize(QtCore.QSize(150, 150))
        self.frame_6.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.Button_save = QtWidgets.QPushButton(self.frame_6)
        self.Button_save.setGeometry(QtCore.QRect(0, 80, 50, 50))
        self.Button_save.setToolTipDuration(-1)
        self.Button_save.setStyleSheet("QPushButton{\n"
                                       "    Border-Radius:0px;\n"
                                       "}\n"
                                       "QPushButton:hover{\n"
                                       "    background-color: rgb(25, 25, 25);\n"
                                       "}\n"
                                       "QPushButton:pressed{\n"
                                       "    background-color: rgb(85, 85, 85);\n"
                                       "}")
        self.Button_save.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(
            ":/Buttons/Buttons/Button_save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_save.setIcon(icon6)
        self.Button_save.setIconSize(QtCore.QSize(40, 40))
        self.Button_save.setAutoRepeat(False)
        self.Button_save.setObjectName("Button_save")
        self.Button_Export = QtWidgets.QPushButton(self.frame_6)
        self.Button_Export.setGeometry(QtCore.QRect(0, 20, 50, 50))
        self.Button_Export.setStyleSheet("QPushButton{\n"
                                         "    Border-Radius:0px;\n"
                                         "}\n"
                                         "QPushButton:hover{\n"
                                         "    background-color: rgb(25, 25, 25);\n"
                                         "}\n"
                                         "QPushButton:pressed{\n"
                                         "    background-color: rgb(85, 85, 85);\n"
                                         "}")
        self.Button_Export.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(
            ":/Buttons/Buttons/Button_export.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_Export.setIcon(icon7)
        self.Button_Export.setIconSize(QtCore.QSize(40, 40))
        self.Button_Export.setAutoRepeat(False)
        self.Button_Export.setObjectName("Button_Export")
        self.verticalLayout_3.addWidget(self.frame_6)
        self.horizontalLayout.addWidget(self.menu_left)
        self.content_right = QtWidgets.QFrame(self.content)
        self.content_right.setStyleSheet("background-color: rgb(60, 60, 60);")
        self.content_right.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.content_right.setFrameShadow(QtWidgets.QFrame.Raised)
        self.content_right.setObjectName("content_right")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.content_right)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Content_Graphics = QtWidgets.QFrame(self.content_right)
        self.Content_Graphics.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.Content_Graphics.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Content_Graphics.setObjectName("Content_Graphics")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.Content_Graphics)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        color = pg.mkColor(60, 60, 60)
        pg.setConfigOption("background", color)
        pg.setConfigOption("foreground", "w")
        pg.setConfigOption("leftButtonPan", True)
        self.graphicsView = pg.PlotWidget(self.Content_Graphics)
        self.graphicsView.setStyleSheet("")
        self.graphicsView.setInputMethodHints(QtCore.Qt.ImhPreferNumbers)
        self.graphicsView.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout_5.addWidget(self.graphicsView)
        self.verticalLayout_2.addWidget(self.Content_Graphics)
        self.Content_erro = QtWidgets.QFrame(self.content_right)
        self.Content_erro.setMinimumSize(QtCore.QSize(0, 55))
        self.Content_erro.setMaximumSize(QtCore.QSize(16777215, 55))
        self.Content_erro.setStyleSheet("")
        self.Content_erro.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Content_erro.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Content_erro.setObjectName("Content_erro")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.Content_erro)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 6)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.frame_Erro = QtWidgets.QFrame(self.Content_erro)
        self.frame_Erro.setMaximumSize(QtCore.QSize(1500, 16777215))
        self.frame_Erro.setStyleSheet("")
        self.frame_Erro.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Erro.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Erro.setObjectName("frame_Erro")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_Erro)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_erro = QtWidgets.QLabel(self.frame_Erro)
        self.label_erro.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_erro.setFont(font)
        self.label_erro.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_erro.setStyleSheet("background-color: rgb(255, 15, 79);\n"
                                      "border-radius:5px;\n"
                                      "color: rgb(255, 255, 255);")
        self.label_erro.setAlignment(QtCore.Qt.AlignCenter)
        self.label_erro.setObjectName("label_erro")
        self.verticalLayout_4.addWidget(self.label_erro)
        self.horizontalLayout_3.addWidget(self.frame_Erro)
        self.frame_SeguirBack = QtWidgets.QFrame(self.Content_erro)
        self.frame_SeguirBack.setMaximumSize(QtCore.QSize(150, 16777215))
        self.frame_SeguirBack.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_SeguirBack.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_SeguirBack.setObjectName("frame_SeguirBack")
        self.Button_back = QtWidgets.QPushButton(self.frame_SeguirBack)
        self.Button_back.setGeometry(QtCore.QRect(20, 0, 50, 50))
        self.Button_back.setStyleSheet("QPushButton{\n"
                                       "    Border-Radius:0px;\n"
                                       "}\n"
                                       "QPushButton:hover{\n"
                                       "    \n"
                                       "    background-color: rgb(100, 100, 100);\n"
                                       "}\n"
                                       "QPushButton:pressed{\n"
                                       "    background-color: rgb(85, 85, 85);\n"
                                       "}")
        self.Button_back.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(
            ":/Buttons/Buttons/Button_back.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_back.setIcon(icon8)
        self.Button_back.setIconSize(QtCore.QSize(40, 40))
        self.Button_back.setAutoRepeat(False)
        self.Button_back.setObjectName("Button_back")
        self.Button_Ok = QtWidgets.QPushButton(self.frame_SeguirBack)
        self.Button_Ok.setGeometry(QtCore.QRect(80, 0, 50, 50))
        self.Button_Ok.setStyleSheet("QPushButton{\n"
                                     "    Border-Radius:0px;\n"
                                     "}\n"
                                     "QPushButton:hover{\n"
                                     "    \n"
                                     "    background-color: rgb(100, 100, 100);\n"
                                     "}\n"
                                     "QPushButton:pressed{\n"
                                     "    background-color: rgb(85, 85, 85);\n"
                                     "}")
        self.Button_Ok.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(
            ":/Buttons/Buttons/Button_ok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_Ok.setIcon(icon9)
        self.Button_Ok.setIconSize(QtCore.QSize(40, 40))
        self.Button_Ok.setAutoRepeat(False)
        self.Button_Ok.setObjectName("Button_Ok")
        self.label_pg = QtWidgets.QLabel(self.frame_SeguirBack)
        self.label_pg.setGeometry(QtCore.QRect(130, 30, 16, 16))
        self.label_pg.setObjectName("label_pg")
        self.horizontalLayout_3.addWidget(self.frame_SeguirBack)
        self.verticalLayout_2.addWidget(self.Content_erro)
        self.horizontalLayout.addWidget(self.content_right)
        self.verticalLayout.addWidget(self.content)
        MainWindow.setCentralWidget(self.centralwidget)

        #
        # FUNÇÕES
        #

        # Desabalita buttons
        self.label_pg.hide()
        self.label_pg.setText("0")
        self.exibicao()

        # Chama a função abrir gráfico
        self.Button_Open.clicked.connect(self.buttonOpen)

        # Altera numeros de pontos no gráfico
        self.pushButton_Add_2.clicked.connect(self.buttonOk)
        self.pushButton_restart_2.clicked.connect(self.resetarpontos)

        # Chama a função para suavizar o gráfico
        self.Button_Suavizar.clicked.connect(self.buttonsuavizargrafico)

        # Remove ou reseta os harmônicos
        self.pushButton_Add.clicked.connect(self.delhamonicos)
        self.pushButton_restart.clicked.connect(self.resetHarmonicos)

        # Plota o gráfico final
        self.Button_Ok.clicked.connect(self.buttonseguir)
        self.Button_back.clicked.connect(self.buttonBack)

        # Salva uma imagem do gráfico
        self.Button_save.clicked.connect(self.salvarImagem)
        self.retranslateUi(MainWindow)

        # Exporta os dados do gráfico
        self.Button_Export.clicked.connect(self.exportarDadosgrafico)

        # Faz a ttf no gráfico em exibição
        self.Button_Fft.clicked.connect(self.fft)

        self.Button_Sobre.clicked.connect(self.sobre)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SurvGraph"))
        self.Button_Open.setToolTip(_translate(
            "MainWindow", "Abrir dados do gráfico"))
        self.groupBox.setTitle(_translate("MainWindow", "Interpolação"))
        self.pushButton_Add_2.setText(_translate("MainWindow", "OK"))
        self.label_quantidade.setText(_translate(
            "MainWindow", "Quantidade de pontos:"))
        self.pushButton_restart_2.setToolTip(
            _translate("MainWindow", "Resetar número de pontos"))
        self.radioButton.setText(_translate("MainWindow", "1º"))
        self.radioButton_2.setText(_translate("MainWindow", "2º"))
        self.radioButton_3.setText(_translate("MainWindow", "3º"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Recorte"))
        self.pushButton_Add.setToolTip(_translate(
            "MainWindow", "recortar ou remover intervalo"))
        self.pushButton_Add.setText(_translate("MainWindow", "Ok"))
        self.label_inter.setText(_translate("MainWindow", "Intervalo : De"))
        self.pushButton_restart.setToolTip(
            _translate("MainWindow", "Resetar intervalos"))
        self.label_ate.setText(_translate("MainWindow", "até"))
        self.Button_Fft.setToolTip(_translate(
            "MainWindow", "Transformada de Fourier do Gráfico"))
        self.Button_Suavizar.setToolTip(
            _translate("MainWindow", " Suavizar o gráfico"))
        self.Button_Sobre.setToolTip(
            _translate("MainWindow", "Sobre o software"))
        self.Button_save.setToolTip(_translate("MainWindow", "Salvar Figura"))
        self.Button_Export.setToolTip(_translate(
            "MainWindow", "Exportar dados do gráfico"))
        self.label_erro.setText(_translate("MainWindow", "Informativo"))
        self.Button_back.setToolTip(_translate("MainWindow", "voltar"))
        self.Button_Ok.setToolTip(_translate("MainWindow", "seguir"))
        self.label_pg.setText(_translate("MainWindow", "TextLabel"))


class Ui_SobreWindow(object):
    def setupUi(self, SobreWindow):
        SobreWindow.setObjectName("SobreWindow")
        SobreWindow.resize(400, 384)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Buttons/ico.ico"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SobreWindow.setWindowIcon(icon)
        SobreWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(SobreWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setStyleSheet("background-color: rgb(60, 60, 60);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label_logo = QtWidgets.QLabel(self.frame)
        self.label_logo.setGeometry(QtCore.QRect(110, 10, 181, 40))
        self.label_logo.setMinimumSize(QtCore.QSize(0, 40))
        self.label_logo.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_logo.setFont(font)
        self.label_logo.setStyleSheet("color: rgb(255, 255, 255);\n"
                                      "border:0px;")
        self.label_logo.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_logo.setText("")
        self.label_logo.setPixmap(QtGui.QPixmap(":/Buttons/Buttons/surv.png"))
        self.label_logo.setScaledContents(True)
        self.label_logo.setObjectName("label_logo")
        self.label_logo_2 = QtWidgets.QLabel(self.frame)
        self.label_logo_2.setGeometry(QtCore.QRect(30, 260, 201, 131))
        self.label_logo_2.setMinimumSize(QtCore.QSize(0, 0))
        self.label_logo_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_logo_2.setFont(font)
        self.label_logo_2.setStyleSheet("color: rgb(255, 255, 255);\n"
                                        "border:0px;")
        self.label_logo_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_logo_2.setText("")
        self.label_logo_2.setPixmap(
            QtGui.QPixmap(":/Buttons/Buttons/brasao.png"))
        self.label_logo_2.setScaledContents(True)
        self.label_logo_2.setObjectName("label_logo_2")
        self.label_logo_3 = QtWidgets.QLabel(self.frame)
        self.label_logo_3.setGeometry(QtCore.QRect(230, 280, 91, 91))
        self.label_logo_3.setMinimumSize(QtCore.QSize(0, 0))
        self.label_logo_3.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_logo_3.setFont(font)
        self.label_logo_3.setStyleSheet("color: rgb(255, 255, 255);\n"
                                        "border:0px;")
        self.label_logo_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_logo_3.setText("")
        self.label_logo_3.setPixmap(QtGui.QPixmap(
            ":/Buttons/Buttons/Logo-HidroUFF-Tipo2_2020.png"))
        self.label_logo_3.setScaledContents(True)
        self.label_logo_3.setObjectName("label_logo_3")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(0, 110, 401, 111))
        font = QtGui.QFont()
        font.setFamily("Poor Richard")
        font.setPointSize(10)
        font.setItalic(False)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(180, 50, 47, 13))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(0, 219, 401, 31))
        font = QtGui.QFont()
        font.setFamily("Poor Richard")
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.frame)
        SobreWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(SobreWindow)
        QtCore.QMetaObject.connectSlotsByName(SobreWindow)

    def retranslateUi(self, SobreWindow):
        _translate = QtCore.QCoreApplication.translate
        SobreWindow.setWindowTitle(_translate(
            "SobreWindow", "Sobre - SurvGraph"))
        self.label.setText(_translate("SobreWindow", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600; color:#ffffff;\">Desenvolvedor:</span></p><p align=\"center\"><span style=\" font-weight:600; color:#ffffff;\">Rodrigo Junior dos Santos Neves</span></p><p align=\"center\"><span style=\" font-weight:600; color:#ffffff;\">Orientador:</span></p><p align=\"center\"><span style=\" font-weight:600; color:#ffffff;\">Profº Gabriel Nascimento</span></p><p align=\"center\"><span style=\" font-weight:600; color:#ffffff;\"><br/></span></p></body></html>"))
        self.label_2.setText(_translate(
            "SobreWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; color:#ffffff;\">V 1.6</span></p></body></html>"))
        self.label_3.setText(_translate(
            "SobreWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; font-weight:600; color:#ffffff;\">Última revisão: 19/08/2020</span></p></body></html>"))


class Ui_ExportWindow(object):

    # Define os parâmetros de exportação de textos
    def confirmar(self):

        XY = ui_main.caminhoparasalvargrafico()  # Chama a funsão da classe principal

        casax = self.spinBox_X.value()
        casay = self.spinBox_Y.value()

        X = XY[0][0]
        Y = XY[0][1]

        if ui_main.label_pg.text() != "2":

            # Verifica qual o separador decimal
            if self.radioButton.isChecked():
                for i in range(len(X)):
                    X[i] = round(X[i], casax)
                    Y[i] = round(Y[i], casay)

            elif self.radioButton_2.isChecked():

                for i in range(len(X)):
                    X[i] = str(round(X[i], casax)).replace(".", ",")
                    Y[i] = str(round(Y[i], casay)).replace(".", ",")

        filename = QtWidgets.QFileDialog.getSaveFileName(
            None, "", ".", "Arquivo de texto (*.txt);; Arquivo CSV (*.csv)"
        )

        try:
            ui_main.writecoordfiles(X, Y, filename[0])
            ui_main.label_erro.setText("Dados exportados com sucesso!")
            ExportWindow.close()
        except FileNotFoundError:
            pass

    def setupUi(self, ExportWindow):
        ExportWindow.setObjectName("ExportWindow")
        ExportWindow.resize(352, 200)
        ExportWindow.setMinimumSize(QtCore.QSize(352, 200))
        ExportWindow.setMaximumSize(QtCore.QSize(352, 200))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Buttons/Buttons/ico.ico"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ExportWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(ExportWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_Formata = QtWidgets.QFrame(self.centralwidget)
        self.frame_Formata.setStyleSheet("background-color: rgb(60, 60, 60);")
        self.frame_Formata.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Formata.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Formata.setObjectName("frame_Formata")
        self.groupBox_Decimal = QtWidgets.QGroupBox(self.frame_Formata)
        self.groupBox_Decimal.setGeometry(QtCore.QRect(10, 50, 141, 71))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_Decimal.setFont(font)
        self.groupBox_Decimal.setStyleSheet("color: rgb(255, 255, 255);")
        self.groupBox_Decimal.setObjectName("groupBox_Decimal")
        self.spinBox_X = QtWidgets.QSpinBox(self.groupBox_Decimal)
        self.spinBox_X.setGeometry(QtCore.QRect(10, 40, 41, 22))
        self.spinBox_X.setMinimumSize(QtCore.QSize(0, 0))
        self.spinBox_X.setProperty("value", 0)
        self.spinBox_X.setObjectName("spinBox_X")
        self.spinBox_Y = QtWidgets.QSpinBox(self.groupBox_Decimal)
        self.spinBox_Y.setGeometry(QtCore.QRect(90, 40, 42, 22))
        self.spinBox_Y.setObjectName("spinBox_Y")
        self.label_X = QtWidgets.QLabel(self.groupBox_Decimal)
        self.label_X.setGeometry(QtCore.QRect(20, 20, 16, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_X.setFont(font)
        self.label_X.setObjectName("label_X")
        self.label_Y = QtWidgets.QLabel(self.groupBox_Decimal)
        self.label_Y.setGeometry(QtCore.QRect(100, 20, 16, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_Y.setFont(font)
        self.label_Y.setObjectName("label_Y")
        self.label_Text = QtWidgets.QLabel(self.frame_Formata)
        self.label_Text.setGeometry(QtCore.QRect(-10, 10, 371, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label_Text.setFont(font)
        self.label_Text.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_Text.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_Text.setAlignment(QtCore.Qt.AlignCenter)
        self.label_Text.setObjectName("label_Text")
        self.groupBox_Separador = QtWidgets.QGroupBox(self.frame_Formata)
        self.groupBox_Separador.setGeometry(QtCore.QRect(190, 50, 141, 71))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_Separador.setFont(font)
        self.groupBox_Separador.setStyleSheet("color: rgb(255, 255, 255);")
        self.groupBox_Separador.setObjectName("groupBox_Separador")
        self.widget = QtWidgets.QWidget(self.groupBox_Separador)
        self.widget.setGeometry(QtCore.QRect(30, 20, 72, 42))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.radioButton = QtWidgets.QRadioButton(self.widget)
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName("radioButton")
        self.verticalLayout.addWidget(self.radioButton)
        self.radioButton_2 = QtWidgets.QRadioButton(self.widget)
        self.radioButton_2.setObjectName("radioButton_2")
        self.verticalLayout.addWidget(self.radioButton_2)
        self.Button_Ok = QtWidgets.QPushButton(self.frame_Formata)
        self.Button_Ok.setGeometry(QtCore.QRect(280, 130, 50, 50))
        self.Button_Ok.setStyleSheet("QPushButton{\n"
                                     "    Border-Radius:0px;\n"
                                     "}\n"
                                     "QPushButton:hover{\n"
                                     "    \n"
                                     "    background-color: rgb(100, 100, 100);\n"
                                     "}\n"
                                     "QPushButton:pressed{\n"
                                     "    background-color: rgb(85, 85, 85);\n"
                                     "}")
        self.Button_Ok.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(
            ":/Buttons/Buttons/Button_ok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_Ok.setIcon(icon1)
        self.Button_Ok.setIconSize(QtCore.QSize(40, 40))
        self.Button_Ok.setAutoRepeat(False)
        self.Button_Ok.setObjectName("Button_Ok")
        self.horizontalLayout.addWidget(self.frame_Formata)
        ExportWindow.setCentralWidget(self.centralwidget)

        self.Button_Ok.clicked.connect(self.confirmar)

        self.retranslateUi(ExportWindow)
        QtCore.QMetaObject.connectSlotsByName(ExportWindow)

    def retranslateUi(self, ExportWindow):
        _translate = QtCore.QCoreApplication.translate
        ExportWindow.setWindowTitle(_translate("ExportWindow", "Survgraph"))
        self.groupBox_Decimal.setTitle(
            _translate("ExportWindow", "Casas decimais"))
        self.label_X.setText(_translate("ExportWindow", "X"))
        self.label_Y.setText(_translate("ExportWindow", "Y"))
        self.label_Text.setText(_translate(
            "ExportWindow", "Formatação de exportação"))
        self.groupBox_Separador.setTitle(
            _translate("ExportWindow", "Separador decimal"))
        self.radioButton.setText(_translate("ExportWindow", "Ponto (.)"))
        self.radioButton_2.setText(_translate("ExportWindow", "Vírgula (,)"))
        self.Button_Ok.setToolTip(_translate("ExportWindow", "Confirmar"))


class Ui_GrafWindow(object):
    ax = ''
    # Exibi uma amostra do gráfico antes de salvar

    def novafigura(self):
        global ax
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        self.atualizarGrap()

    # Função para retornar a cor da linha
    def definir_cor(self, cor):
        if cor == "Azul":
            cor = 'b'
        elif cor == "Vermelho":
            cor = 'r'
        elif cor == "Verde":
            cor = 'g'
        elif cor == "Ciano":
            cor = 'c'
        elif cor == "Magenta":
            cor = 'm'
        elif cor == "Amarelo":
            cor = 'y'
        elif cor == "Preto":
            cor = 'k'
        else:
            cor = 'gray'
        return cor

    def atualizarGrap(self):
        global ax
        esp_linha = self.doubleSpinBox_linha.value()
        esp_grad = self.doubleSpinBox_Grade.value()
        cor_linha = self.definir_cor(self.comboBox_Linha.currentText())
        cor_grade = self.definir_cor(self.comboBox_Grade.currentText())

        dados = ui_main.caminhoparasalvargrafico()
        XY = dados[0]
        ax.clear()

        if ui_main.label_pg.text() == ("4"):
            plt.title("Transformada de Fourier")
            plt.xlabel("Frequência (Hz)")
            plt.ylabel("Amplitude")
            ax.bar(XY[0], XY[1], width=esp_linha, color=cor_linha)
            self.groupBox.setTitle("Barras")
        elif dados[1] == "plot":
            ax.plot(XY[0], XY[1], linewidth=esp_linha, color=cor_linha)
            self.groupBox.setTitle("Linha")
        else:
            ax.bar(XY[0], XY[1],  width=esp_linha, color=cor_linha)
            self.groupBox.setTitle("Barras")

        plt.grid(color=cor_grade, linestyle="-", linewidth=esp_grad)
        plt.show()

    # Salva o gráfico em alta qualidade
    def salvargrafico(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(
            None, "Salvar imagem do gráfico", "ImgSurvGraph",
            "*.eps;; *.pdf;; *.pgf;; *.png;; *.ps;; *.raw;; *.rgba;; \
                *.svg;; *.svgz"
        )
        try:
            plt.savefig(filename[0], dpi=1000)
            ui_main.label_erro.setText(
                "Print do gráfico salvo com sucesso!")
            plt.close()
            GrafWindow.close()

        except FileNotFoundError:
            pass

    def setupUi(self, GrafWindow):
        GrafWindow.setObjectName("GrafWindow")
        GrafWindow.resize(262, 233)
        GrafWindow.setMinimumSize(QtCore.QSize(262, 233))
        GrafWindow.setMaximumSize(QtCore.QSize(262, 233))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Buttons/Buttons/ico.ico"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        GrafWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(GrafWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setStyleSheet("background-color: rgb(60, 60, 60);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.groupBox = QtWidgets.QGroupBox(self.frame)
        self.groupBox.setGeometry(QtCore.QRect(20, 20, 91, 141))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setStyleSheet("color: rgb(255, 255, 255);")
        self.groupBox.setObjectName("groupBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 20, 47, 13))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.comboBox_Linha = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_Linha.setGeometry(QtCore.QRect(10, 40, 69, 22))
        self.comboBox_Linha.setObjectName("comboBox_Linha")
        self.comboBox_Linha.addItem("")
        self.comboBox_Linha.addItem("")
        self.comboBox_Linha.addItem("")
        self.comboBox_Linha.addItem("")
        self.comboBox_Linha.addItem("")
        self.comboBox_Linha.addItem("")
        self.comboBox_Linha.addItem("")
        self.comboBox_Linha.addItem("")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(10, 80, 71, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.doubleSpinBox_linha = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_linha.setGeometry(QtCore.QRect(10, 100, 62, 22))
        self.doubleSpinBox_linha.setDecimals(3)
        self.doubleSpinBox_linha.setMaximum(10.0)
        self.doubleSpinBox_linha.setSingleStep(0.1)
        self.doubleSpinBox_linha.setProperty("value", 1.0)
        self.doubleSpinBox_linha.setObjectName("doubleSpinBox_linha")
        self.Button_Ok_2 = QtWidgets.QPushButton(self.frame)
        self.Button_Ok_2.setGeometry(QtCore.QRect(190, 170, 50, 50))
        self.Button_Ok_2.setStyleSheet("QPushButton{\n"
                                       "    Border-Radius:0px;\n"
                                       "}\n"
                                       "QPushButton:hover{\n"
                                       "    \n"
                                       "    background-color: rgb(100, 100, 100);\n"
                                       "}\n"
                                       "QPushButton:pressed{\n"
                                       "    background-color: rgb(85, 85, 85);\n"
                                       "}")
        self.Button_Ok_2.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(
            ":/Buttons/Buttons/Button_ok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_Ok_2.setIcon(icon1)
        self.Button_Ok_2.setIconSize(QtCore.QSize(40, 40))
        self.Button_Ok_2.setAutoRepeat(False)
        self.Button_Ok_2.setObjectName("Button_Ok_2")
        self.groupBox_2 = QtWidgets.QGroupBox(self.frame)
        self.groupBox_2.setGeometry(QtCore.QRect(140, 20, 101, 141))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setStyleSheet("color: rgb(255, 255, 255);")
        self.groupBox_2.setObjectName("groupBox_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(10, 20, 47, 13))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.comboBox_Grade = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_Grade.setGeometry(QtCore.QRect(10, 40, 69, 22))
        self.comboBox_Grade.setObjectName("comboBox_Grade")
        self.comboBox_Grade.addItem("")
        self.comboBox_Grade.addItem("")
        self.comboBox_Grade.addItem("")
        self.comboBox_Grade.addItem("")
        self.comboBox_Grade.addItem("")
        self.comboBox_Grade.addItem("")
        self.comboBox_Grade.addItem("")
        self.comboBox_Grade.addItem("")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setGeometry(QtCore.QRect(10, 80, 71, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.doubleSpinBox_Grade = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_Grade.setGeometry(QtCore.QRect(10, 100, 62, 22))
        self.doubleSpinBox_Grade.setDecimals(3)
        self.doubleSpinBox_Grade.setMaximum(10.0)
        self.doubleSpinBox_Grade.setSingleStep(0.1)
        self.doubleSpinBox_Grade.setProperty("value", 0.5)
        self.doubleSpinBox_Grade.setObjectName("doubleSpinBox_Grade")
        self.verticalLayout.addWidget(self.frame)
        GrafWindow.setCentralWidget(self.centralwidget)

        "#########Funções###########"

        self.comboBox_Grade.activated.connect(self.atualizarGrap)
        self.comboBox_Linha.activated.connect(self.atualizarGrap)
        self.doubleSpinBox_Grade.valueChanged.connect(self.atualizarGrap)
        self.doubleSpinBox_linha.textChanged.connect(self.atualizarGrap)
        self.Button_Ok_2.clicked.connect(self.salvargrafico)
        ###########################################################
        self.retranslateUi(GrafWindow)
        QtCore.QMetaObject.connectSlotsByName(GrafWindow)

    def retranslateUi(self, GrafWindow):
        _translate = QtCore.QCoreApplication.translate
        GrafWindow.setWindowTitle(_translate("GrafWindow", "SurvGraph"))
        self.groupBox.setTitle(_translate("GrafWindow", "Barras"))
        self.label.setText(_translate("GrafWindow", "Cor"))
        self.comboBox_Linha.setItemText(0, _translate("GrafWindow", "Azul"))
        self.comboBox_Linha.setItemText(
            1, _translate("GrafWindow", "Vermelho"))
        self.comboBox_Linha.setItemText(2, _translate("GrafWindow", "Verde"))
        self.comboBox_Linha.setItemText(3, _translate("GrafWindow", "Ciano"))
        self.comboBox_Linha.setItemText(4, _translate("GrafWindow", "Magenta"))
        self.comboBox_Linha.setItemText(5, _translate("GrafWindow", "Amarelo"))
        self.comboBox_Linha.setItemText(6, _translate("GrafWindow", "Preto"))
        self.comboBox_Linha.setItemText(7, _translate("GrafWindow", "Cinza"))
        self.label_3.setText(_translate("GrafWindow", "Espessura"))
        self.groupBox_2.setTitle(_translate("GrafWindow", "Linha de grade"))
        self.label_2.setText(_translate("GrafWindow", "Cor"))
        self.comboBox_Grade.setItemText(0, _translate("GrafWindow", "Cinza"))
        self.comboBox_Grade.setItemText(1, _translate("GrafWindow", "Azul"))
        self.comboBox_Grade.setItemText(
            2, _translate("GrafWindow", "Vermelho"))
        self.comboBox_Grade.setItemText(3, _translate("GrafWindow", "Verde"))
        self.comboBox_Grade.setItemText(4, _translate("GrafWindow", "Ciano"))
        self.comboBox_Grade.setItemText(5, _translate("GrafWindow", "Magenta"))
        self.comboBox_Grade.setItemText(6, _translate("GrafWindow", "Amarelo"))
        self.comboBox_Grade.setItemText(7, _translate("GrafWindow", "Preto"))
        self.label_4.setText(_translate("GrafWindow", "Espessura"))
        self.Button_Ok_2.setToolTip(_translate("GrafWindow", "Confirmar"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui_main = Ui_MainWindow()
    ui_main.setupUi(MainWindow)

    SobreWindow = QtWidgets.QMainWindow()
    ui_sobre = Ui_SobreWindow()
    ui_sobre.setupUi(SobreWindow)

    ExportWindow = QtWidgets.QMainWindow()
    ui_export = Ui_ExportWindow()
    ui_export.setupUi(ExportWindow)

    GrafWindow = QtWidgets.QMainWindow()
    ui_graf = Ui_GrafWindow()
    ui_graf.setupUi(GrafWindow)

    MainWindow.show()
    sys.exit(app.exec_())
