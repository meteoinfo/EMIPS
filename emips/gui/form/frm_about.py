# coding=utf-8

import os

from javax import swing


class FrmAbout(swing.JDialog):

    def __init__(self, frm_main, model):
        super(FrmAbout, self).__init__(frm_main, model)

        self.frm_main = frm_main
        self.title = "About EMIPS"
        self.init_gui()

    def init_gui(self):
        # Icon image
        icon = swing.ImageIcon(os.path.join(self.frm_main.current_path, 'image', 'emission.jpg'))
        label_icon = swing.JLabel()
        label_icon.setIcon(icon)

        # Full name of EMIPS
        label_full_name = swing.JLabel("EMission Inventory Processing System")

        # Version
        label_version = swing.JLabel("Version: 1.0")

        # Author
        label_author = swing.JLabel("Author: Yaqiang Wang & Wenchong Chen")

        # Email
        label_email = swing.JLabel("Email: yaqiang.wang@gmail.com")

        # Website
        label_website = swing.JLabel("Website: http://www.meteothink.org")

        # Layout
        layout = swing.GroupLayout(self.contentPane)
        self.contentPane.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        layout.setHorizontalGroup(
            layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
            .addComponent(label_icon)
            .addComponent(label_full_name)
            .addGap(15)
            .addComponent(label_version)
            .addComponent(label_author)
            .addComponent(label_email)
            .addComponent(label_website)
            .addGap(20)
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
            .addComponent(label_icon)
            .addComponent(label_full_name)
            .addGap(15)
            .addComponent(label_version)
            .addComponent(label_author)
            .addComponent(label_email)
            .addComponent(label_website)
            .addGap(20)
        )

        self.setResizable(False)
        self.pack()
