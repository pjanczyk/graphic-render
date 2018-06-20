from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QApplication


class QtImageViewer(QGraphicsView):
    def __init__(self, image: QImage):
        QGraphicsView.__init__(self)

        pixmap = QPixmap.fromImage(image)

        scene = QGraphicsScene()
        scene.addPixmap(pixmap)

        self.setScene(scene)
        self.setSceneRect(QRectF(pixmap.rect()))

        self.update_viewer()

    def update_viewer(self):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        self.update_viewer()


def show_image_viewer(image: QImage):
    app = QApplication([])

    viewer = QtImageViewer(image)
    viewer.show()

    exit_code = app.exec()
    app.deleteLater()
    return exit_code
