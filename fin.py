from kivymd.app import MDApp
from kivy.lang import Builder
import cv2
import numpy as np
import glob, os
from imutils import contours
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivymd.uix.list import OneLineAvatarIconListItem
from kivy.core.window import Window
from pyfirmata import Arduino

board = Arduino('COM3')

class Errorpop(Popup):
    text = StringProperty("")

class MyPopup(Popup):
    pass

#class ListItemWithCheckBox(OneLineAvatarIconListItem):
    #pass


class MyApp(MDApp):
    path_matrix = r'C:\Users\OWNER\Desktop\Thesis_final\Thesis app\visa-matrix.gif'
    path_template = r'C:\Users\OWNER\Desktop\Thesis_final\zee.jpg'

    def on_light(self):
        board.digital[13].write(1)

    def off_light(self):
        board.digital[13].write(0)

    def resize(self,image, width=None, height=None, inter=cv2.INTER_AREA):
        dim = None
        (h, w) = image.shape[:2]
        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))
        resized = cv2.resize(image, dim, interpolation=inter)
        return resized
        
    def sort_contours(self, cnts, method="left-to-right"):
        reverse = False
        i = 0
        if method == "right-to-left" or method == "bottom-to-top":
            reverse = True
        if method == "top-to-bottom" or method == "bottom-to-top":
            i = 1
        Boundingboxes = [cv2.boundingRect(c) for c in cnts]  # use the smallest rectangle to wrap the found shape x, y, h, W
        (cnts, Boundingboxes) = zip(*sorted(zip(cnts, Boundingboxes),
                                            key=lambda b: b[1][i], reverse=reverse))
        return cnts, Boundingboxes
        
    def get_process(self):
        err = Errorpop()
        if self.root.ids.image_cap.source == self.path_matrix:
            #print("Please load image before process!")
            err.text = "Please load image before process!"
            err.open()
        else:
            try:
                # Location of credit card
                #predict_card = r"C:\Users\franc\Pictures\credit card numbers\card100.jpg"
                #predict_card = r"C:\Users\franc\Pictures\credit card numbers\thesis_card.jpg"
                predict_card = self.root.ids.image_cap.source
                # Location of template
                #template = r"C:\Users\franc\Pictures\credit card numbers\bingpong122.jpg"
                template = self.path_template
                
                FIRST_NUMBER = {
                "3": "American Express",
                "4": "Visa",
                "5": "MasterCard",
                "6": "Discover Card"
                }
                img = cv2.imread(template)
                ref = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                ref = cv2.threshold(ref, 10, 255, cv2.THRESH_BINARY_INV)[1]
                refCnts, hierarchy = cv2.findContours(ref.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(img, refCnts, -1, (0, 0, 255), 3)
                print(np.array(refCnts).shape) 
                # Sort, left to right, top to bottom
                refCnts = self.sort_contours(refCnts, method="left-to-right")[0]
                digits = {}
                for (i, c) in enumerate(refCnts):
                    # Calculate the bounding rectangle and reshape it to the right size
                    (x, y, w, h) = cv2.boundingRect(c)
                    roi = ref[y:y + h, x:x + w]
                    roi = cv2.resize(roi, (57, 88))
                    # Each number corresponds to each template
                    digits[i] = roi
                rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
                sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                image = cv2.imread(predict_card)
                # First, the image is resized
                '''image here'''
                cv2.imshow('image', image)
                image = self.resize(image, width=300)
                # Gray processing
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                '''gray here'''
                cv2.imshow('gray', gray)
                tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, rectKernel)
                '''tophat here'''
                cv2.imshow('tophat', tophat)
                gradX = cv2.Sobel(tophat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
                gradX = np.absolute(gradX)
                (minVal, maxVal) = (np.min(gradX), np.max(gradX))
                gradX = (255 * ((gradX - minVal) / (maxVal - minVal)))
                gradX = gradX.astype("uint8")
                print(np.array(gradX).shape)
                '''gradx here'''
                cv2.imshow('gradx', gradX)
                gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
                thresh = cv2.threshold(gradX, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
                '''thresh here'''
                cv2.imshow('thresh', thresh)
                threshCnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = threshCnts
                cur_img = image.copy()
                cv2.drawContours(cur_img, cnts, -1, (0, 0, 255), 3)
                '''cur here'''
                cv2.imshow('cur image', cur_img)
                locs = []
                # Traversal profile
                for (i, c) in enumerate(cnts):
                    # Calculate rectangle
                    (x, y, w, h) = cv2.boundingRect(c)
                    ar = w / float(h)
                    # Choose the right area, according to the actual task, here are basically a group of four numbers
                    if ar > 2.5 and ar < 4.0:
                        if (w > 40 and w < 55) and (h > 10 and h < 20):
                            # The right ones stay
                            locs.append((x, y, w, h))
                # Sort the matched profiles from left to right
                locs = sorted(locs, key=lambda x: x[0])
                output = []
                for (i, (gX, gY, gW, gH)) in enumerate(locs):
                    # initialize the list of group digits
                    groupOutput = []
                    # Extract each group according to the coordinates
                    group = gray[gY - 5:gY + gH + 5, gX - 5:gX + gW + 5]
                    '''group here'''
                    cv2.imshow('group', group)
                    # Pretreatment
                    group = cv2.threshold(group, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                    '''group thresh here'''
                    cv2.imshow('group threshold', group)
                    # Calculate the contour of each group
                    digitCnts, hierarchy = cv2.findContours(group.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    digitCnts = contours.sort_contours(digitCnts, method="left-to-right")[0]
                    # Calculate each value in each group
                    for c in digitCnts:
                        # Find the contour of the current value and reset to the appropriate size
                        (x, y, w, h) = cv2.boundingRect(c)
                        roi = group[y:y + h, x:x + w]
                        roi = cv2.resize(roi, (57, 88))
                        '''roi here'''
                        cv2.imshow('roi', roi)
                        # Calculate match score
                        scores = []
                        # Calculate each score in the template
                        for (digit, digitROI) in digits.items():
                            # Template matching
                            result = cv2.matchTemplate(roi, digitROI, cv2.TM_CCOEFF)
                            (_, score, _, _) = cv2.minMaxLoc(result)
                            scores.append(score)
                        # Get the most appropriate number
                        groupOutput.append(str(np.argmax(scores)))
                    # Draw it
                    cv2.rectangle(image, (gX - 5, gY - 5), (gX + gW + 5, gY + gH + 5), (0, 255, 0), 1)
                    cv2.putText(image, "".join(groupOutput), (gX-1, gY + 37), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
                    # Get the results
                    output.extend(groupOutput)
                    ben = (format("".join(output)))
                    int(ben)
                    print("Credit Card Type: {}".format(FIRST_NUMBER[output[0]]))
                    print("Credit Card #: {}".format("".join(output)))
                    print(ben)
                    cv2.imshow("processed image", image)
                    if (self.checkLuhn(ben)):
                        print("Real Credit Card")
                        self.root.ids.result.text = f"#{ben}\n{FIRST_NUMBER[ben[0]]}\nReal Credit Card."
                    else:
                        print("Fake Credit Card")
                        self.root.ids.result.text = f"#{ben}\n{FIRST_NUMBER[ben[0]]}\nFake Credit Card."
        
            except Exception as e:
                err.text = "invalid image! try again."
                err.open()
                #print("invalid image! try again.")
    def snappy(self):
        print("we have taken picture!")
        #path = r"C:\Users\franc\PycharmProjects\sublimePython\Thesis app"
        path = r"C:\Users\OWNER\Desktop\Thesis_final\Thesis app"
        imglist = []
        for file in glob.iglob(path + "**/*.jpg", recursive=True):
            #print(file)
            imglist.append(file)
        #bork = glob.glob(r"*.jpg")
        #print(bork[-1])
        #self.root.ids.my_list.add_widget(
        #    ListItemWithCheckBox(text=f"{bork[-1]}")
        #)
                 
    def load(self):  
        err = Errorpop()
        #path = r"C:\Users\franc\PycharmProjects\sublimePython\Thesis app"
        path = r"C:\Users\OWNER\Desktop\Thesis_final\Thesis app"
        imglist = []
        for file in glob.iglob(path + "**/*.jpg", recursive=True):
            #print(file)
            imglist.append(file)
        try:
            self.root.ids.image_cap.source = f"{imglist[-1]}"
            #self.root.ids.image_cap.source = r"C:\Users\franc\Pictures\credit card numbers\card100.jpg"
        except Exception as e:
            #print(e)
            err.text = "No image to load. File Empty."
            err.open()
                                
    def load_another_image(self):
        #self.root.ids.image_cap.source = r"C:\Users\franc\Pictures\credit card numbers\card100.jpg"
        self.root.ids.image_cap.source = r"C:\Users\OWNER\Desktop\Thesis_final\Thesis app\2022-06-17 22.43.12.jpg"
    
    def delete(self):
        err = Errorpop()
        #self.root.ids.image_cap.source = ""
        imglist = []
        #path = r"C:\Users\franc\PycharmProjects\sublimePython\Thesis app"
        path = r"C:\Users\OWNER\Desktop\Thesis_final\Thesis app"
        for file in glob.iglob(path + "**/*.jpg", recursive=True):
            #os.remove(file)
            imglist.append(file)
        try:
            if self.root.ids.image_cap.source == self.path_matrix:
                err.text = "Please load image to Delete. Try again."
                err.open()
            else:
                os.remove(imglist[-1])
                self.root.ids.image_cap.source = self.path_matrix
                err.text = "Image have been Deleted."
                err.open()
                #print("file deleted!")
        except Exception as e:
            #err.text = "No image to Delete. File Empty!"
            #err.open()
            print(e)
           
    #def remove_widget(self, widget):
        #self.root.ids.my_list.remove_widget(widget)
        
    def print_image(self):
        bork = glob.glob(r"*.jpg")
        print(bork[-1])
        self.root.ids.image_cap.source = f"{bork[-1]}"
        print("hello world")
                   
    def checkLuhn(self, cardNo):
        nDigits = len(cardNo)
        nSum = 0
        isSecond = False

        for i in range(nDigits - 1, -1, -1):
            d = ord(cardNo[i]) - ord('0')

            if (isSecond == True):
                d = d * 2

            # We add two digits to handle
            # cases that make two digits after
            # doubling
            nSum += d // 10
            nSum += d % 10

            isSecond = not isSecond

        if (nSum % 10 == 0):
            return True
        else:
            return False
    
    def go(self):
        err = Errorpop()
        if self.root.ids.manual.text == "":
            #print("Please enter number.")
            err.text = "Please Enter Number."
            err.open()
        else:
            num = self.root.ids.manual.text
            FIRST_NUMBER = {
            "3": "American Express",
            "4": "Visa",
            "5": "MasterCard",
            "6": "Discover Card"
            }
            if (self.checkLuhn(num)):
                self.root.ids.result.text = f"#{num}\n{FIRST_NUMBER[num[0]]}\nReal Credit Card."        
            else:
                self.root.ids.result.text = f"#{num}\nFake Credit Card."
            
    def clear(self):
        self.root.ids.manual.text = ""
        self.root.ids.result.text = "Card No."
        self.root.ids.image_cap.source = self.path_matrix
    
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        #return Builder.load_file("final_app_ui.kv")
        return Builder.load_string('''
        
#: import XCamera kivy_garden.xcamera.XCamera
<Errorpop>
    auto_dismiss: False
    title: "Message"
    size_hint: 0.4, 0.2
    pos_hint: {"center_x": 0.5,"center_y": 0.5}

    BoxLayout:
        orientation: 'vertical'
        Label:
            id: errmsg
            text: root.text
            size_hint: 1, 0.1
        Button:
            text: "Close"
            size_hint: 1, 0.1
            on_release: root.dismiss()


<MyPopup>
    auto_dismiss: False
    title: "Welcome to login screen!"
    size_hint: 0.5, 0.3
    pos_hint: {"center_x": 0.5,"center_y": 0.5}

    BoxLayout:
        orientation: 'vertical'
        Label:
            id: resu
            text: ""
            size_hint: 1, 0.1
        TextInput:
            id: usa
            size_hint: 1, 0.1
            hint_text: "enter username"
        TextInput:
            id: pasa
            password: True
            size_hint: 1, 0.1
            hint_text: "enter password"

        Button:
            size_hint: 1, 0.1
            text: "login"
            on_release: 
                if usa.text == "admin" and pasa.text == "admin":\
                root.dismiss()
                if usa.text != "admin" and pasa.text !="admin":\
                resu.text = "Failed! try again."


#<ListItemWithCheckBox>
    #on_release: app.print_image()

    #IconRightWidget:
        #icon: "delete"
        #on_release: app.remove_widget(root)




BoxLayout:
    orientation: 'vertical'

    MDToolbar:
        title: "Credit Card Number Checker"

    GridLayout:
        cols: 2
        
        
        XCamera:
            id: camera
            on_picture_taken: app.snappy()

        Image:
            id: image_cap
            source: ""
            allow_stretch: True


        #ScrollView:
            #MDList:
                #id: my_list

    Label:
        id: result
        text: "Card No."
        size_hint: 1, 0.3
    
    Button:
        text: "load image"
        size_hint: 1, 0.1
        on_release: app.load()
        #on_release: app.load_another_image()
    Button:
        text: "process image"
        size_hint: 1, 0.1
        on_release: app.get_process()
    
    Button:
        text: "Delete image"
        size_hint: 1, 0.1
        on_release: app.delete()
    Button:
        text: "On Blue Light"
        size_hint: 1, 0.1
        on_release: app.on_light()
    Button:
        text: "Off Blue Light"
        size_hint: 1, 0.1
        on_release: app.off_light()

    
    TextInput:
        id: manual
        hint_text: "Manual Input"
        multiline: False
        size_hint: 1, 0.1
    
    GridLayout:
        cols:2
        size_hint: 1, 0.1

        Button:
            text: "submit manual"
            size_hint: 1, 0.1
            on_release: app.go()

        Button:
            text: "clear"
            size_hint: 1, 0.1
            on_release: app.clear()
                                   
                                   ''')        
    def on_start(self):
        #bork = glob.glob(r"*.jpg")
        #print(bork[-1])
        #self.root.ids.my_list.add_widget(
        #    ListItemWithCheckBox(text=f"{bork[-1]}")
        #)
        pop = MyPopup()
        pop.open()
        self.root.ids.image_cap.source = self.path_matrix
        return super().on_start()

if __name__=="__main__":  
    MyApp().run()