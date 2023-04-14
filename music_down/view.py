import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextBrowser, QVBoxLayout, QHBoxLayout, QMessageBox, QListWidgetItem, QListWidget, QFileDialog, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from music_down import get_search_result, get_music


class MusicDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('音乐下载器')
        self.setWindowIcon(QIcon('icon.png'))
        self.setGeometry(100, 100, 600, 600)
        self.setMinimumSize(500, 500)
        self.layout = QVBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('输入关键字')
        self.layout.addWidget(self.search_box)

        self.search_button = QPushButton('搜索')
        self.search_button.clicked.connect(self.search_music)
        self.layout.addWidget(self.search_button)

        # 将QTextBrowser改为QListWidget
        self.result_box = QListWidget()
        self.result_box.itemClicked.connect(self.select_item)
        self.layout.addWidget(self.result_box)

        # 添加下载类型的选择框
        self.download_type = QComboBox()
        self.download_type.addItems(['只下载音乐', '只下载歌词', '下载音乐+歌词'])
        self.layout.addWidget(self.download_type)

        # 添加下载路径选择框和浏览按钮
        self.download_path_box = QLineEdit()
        self.download_path_box.setPlaceholderText('选择下载路径')
        self.layout.addWidget(self.download_path_box)
        self.browse_button = QPushButton('浏览')
        self.browse_button.clicked.connect(self.browse_path)
        self.layout.addWidget(self.browse_button)

        self.download_button = QPushButton('下载')
        self.download_button.clicked.connect(self.download_music)
        self.download_button.setEnabled(False)
        self.layout.addWidget(self.download_button)
        self.setLayout(self.layout)

    def browse_path(self):
        # 弹出文件夹选择对话框，选择下载路径并显示在下载路径选择框中
        path = QFileDialog.getExistingDirectory(self, '选择下载路径')
        if path:
            self.download_path_box.setText(path)

    def search_music(self):
        keyword = self.search_box.text()
        result = get_search_result(keyword)
        if result is None:
            QMessageBox.warning(self, '错误', '搜索失败,可能不存在')
        elif isinstance(result, str):
            QMessageBox.information(self, '搜索结果', result)
        else:
            self.result_box.clear()
            for music in result[1]:
                item = QListWidgetItem(music['title'] + ' - ' + music['author'])
                item.setData(Qt.UserRole, music['link'])
                self.result_box.addItem(item)
            self.download_button.setEnabled(True)

    def select_item(self, item):
        self.selected_item = item

    def download_music(self):
        if not hasattr(self, 'selected_item'):
            return
        file_link = self.selected_item.data(Qt.UserRole)
        file_name = self.selected_item.text().split('-')[0].strip()
        music_path = None
        lyric_path = None
        download_type = self.download_type.currentIndex()
        download_path = self.download_path_box.text()

        # 根据下载类型设置下载路径和文件名
        if download_type == 0:  # 只下载音乐
            music_path = os.path.join(download_path, file_name + '.mp3')
        elif download_type == 1:  # 只下载歌词
            lyric_path = os.path.join(download_path, file_name + '.lrc')
        else:  # 下载音乐和歌词
            music_path = os.path.join(download_path, file_name + '.mp3')
            lyric_path = os.path.join(download_path, file_name + '.lrc')

        try:
            music_link = file_link.split('(')[-1].replace(')', '')
            result = get_music(music_link, music_path, lyric_path)
            if result:
                QMessageBox.information(self, '下载完成', '下载完成')
            else:
                QMessageBox.warning(self, '下载失败', '不存在下载链接')
        except Exception as e:
            QMessageBox.warning(self, '下载失败', str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MusicDownloader()
    window.show()
    sys.exit(app.exec_())