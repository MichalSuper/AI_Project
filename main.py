import threading
import time
import winsound
import cv2
import numpy as np
import tkinter as tk
import requests

CONFIDENCE = 0.5
PERSON_ID = 0
NAME = "manager"
CODE = "1111"
suspicious_videos = []
videos = ['01.mp4', '02.mp4', '03.mp4']
turnoff = False
buttons = []

# Set the API credentials
account_sid = 'ACaa5832d1c4b7d0a701ebdb688ad4a433'
auth_token = '34c59acbff90b7569d7cadfff746c96e'

# Set the phone numbers
from_number = '+13088248323'
to_number = '+972535212517'

# Set the message text
message_text = 'Emergency event!!'

classes = None
with open('calasses', 'r') as f:
    classes = [line.strip() for line in f.readlines()]

COLORS = np.random.uniform(0, 255, size=(len(classes), 3))


def get_output_layers(net):
    layer_names = net.getLayerNames()
    try:
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    except:
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    if class_id == PERSON_ID:
        label = str(classes[class_id])
    else:
        label = 'non person'

    label = label + " " + str(round(confidence, 2))

    color = COLORS[class_id]

    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)

    cv2.putText(img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


# show the suspicious video
def show_video():
    # Open the video file
    video_capture = cv2.VideoCapture(VIDEO)

    # Set the frame rate
    frame_rate = 10

    # Loop until the end of the video
    while True:
        # Read the next frame
        success, frame = video_capture.read()

        # Check if the frame was read correctly
        if not success:
            break

        # Display the frame
        cv2.imshow('Video', frame)

        # Wait for the specified number of milliseconds
        cv2.waitKey(200 // frame_rate)

        # Check if the user pressed the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and destroy the window
    video_capture.release()
    cv2.destroyAllWindows()


# play the alarm sound
def play_sound():
    winsound.PlaySound('alarm.wav', winsound.SND_FILENAME)


# send a warning message to the screen and in SMS format
def playAlarm():
    response = requests.post(
        'https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json'.format(account_sid),
        auth=(account_sid, auth_token),
        data={
            'From': from_number,
            'To': to_number,
            'Body': message_text,
        }
    )
    alarm.place(x=510, y=100)
    alarm1.place(x=550, y=150)
    alarm.after(1000, play_sound)
    video_display.place(x=520, y=250)
    mainWindow.update_idletasks()


# go through the video and check if there is more than one person
def people_detection():
    # Open video file or capture device.
    alarm.place_forget()
    alarm1.place_forget()
    video_display.place_forget()
    mainWindow.update()

    cap = cv2.VideoCapture(VIDEO)

    net = cv2.dnn.readNet('yolov3.weights', 'cnfg')

    count = -1
    persons_frames = 0

    while True:
        count += 1
        # Capture frame-by-frame
        ret, image = cap.read()
        if count % 4 > 0:
            continue
        if not ret:
            break
        Width = image.shape[1]
        Height = image.shape[0]
        scale = 0.00392

        blob = cv2.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)

        net.setInput(blob)

        outs = net.forward(get_output_layers(net))

        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.6

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > CONFIDENCE:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        person_count = 0
        for i in indices:
            try:
                box = boxes[i]
            except:
                i = i[0]
                box = boxes[i]

            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            if class_ids[i] == PERSON_ID:
                person_count += 1
            draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x + w), round(y + h))

        if person_count > 1:
            persons_frames += 1
        if persons_frames >= 2:
            playAlarm()
            global suspicious_videos
            suspicious_videos += [VIDEO[:]]
            break

        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.imshow("frame", image)
        if cv2.waitKey(1) >= 0:  # Break with ESC
            break

    cap.release()
    cv2.destroyAllWindows()


# re-watching the video
def replay_video(vname):
    global VIDEO
    VIDEO = vname
    show_video()


# thread that runs the video one after the other and displays output accordingly
class first(threading.Thread):
    def run(self):
        activate.place_forget()
        unactivate.place(x=900, y=50)
        global VIDEO
        global turnoff
        for i in range(len(videos)):
            VIDEO = videos[i]
            if turnoff:
                break
            people_detection()
            time.sleep(12)
        alarm.place_forget()
        alarm1.place_forget()
        video_display.place_forget()
        for i in range(len(suspicious_videos)):
            buttons[i].place(x=520, y=70 * i + 100)


# turns on the camera
def play_camera():
    first().start()


# turns off the camera
def turn_off():
    global turnoff
    turnoff = True
    unactivate.place_forget()


# display the page that activate the camera
def secondwindow():
    if name.get(1.0, "end-1c") == NAME and code.get(1.0, "end-1c") == CODE:
        name.place_forget()
        code.place_forget()
        ok.place_forget()
        code_label.place_forget()
        name_label.place_forget()
        activate.place(x=520, y=250)


# display the login page
def login():
    login_but.place_forget()
    name.place(x=550, y=150)
    name_label.place(x=430, y=150)
    code.place(x=550, y=250)
    code_label.place(x=430, y=250)
    ok.place(x=590, y=350)


# User interface
mainWindow = tk.Tk()
mainWindow.state('zoomed')
mainWindow.title('Color of truth')
mainWindow.config(bg="#000000")

image = tk.PhotoImage(file="image.png")
image_label = tk.Label(mainWindow, image=image, borderwidth=0)
image_label.place(x=50, y=450)

login_but = tk.Button(mainWindow, text="Log in", width=10, height=2, command=login,
                      font=("Tahoma", 18, "bold"), relief="solid", bg="black", fg="white")
login_but.place(x=550, y=250)

name = tk.Text(mainWindow, width=15, height=1, font=("Tahoma", 18, "normal"), bg="black", fg="white")
code = tk.Text(mainWindow, width=15, height=1, font=("Tahoma", 18, "normal"), bg="black", fg="white")
ok = tk.Button(mainWindow, text="ok", width=5, height=1, command=secondwindow,
               font=("Tahoma", 18, "bold"), relief="solid", bg="black", fg="white")
name_label = tk.Label(text="user name:", font=("Tahoma", 14, "bold"), bg="black", fg="white")
code_label = tk.Label(text="password:", font=("Tahoma", 14, "bold"), bg="black", fg="white")
activate = tk.Button(mainWindow, text="Activate Camera", width=15, height=2, command=play_camera,
                     font=("Tahoma", 18, "bold"), relief="solid", bg="black", fg="white")

alarm = tk.Label(text="WARNING!!!", font=("Tahoma", 30, "bold"), bg="black", fg="red")
alarm1 = tk.Label(text="Camera 020201", font=("Tahoma", 14, "bold"), bg="black", fg="white")
video_display = tk.Button(mainWindow, text="Show Video", width=15, height=2, command=show_video,
                          font=("Tahoma", 18, "bold"), relief="solid", bg="black", fg="white")
unactivate = tk.Button(mainWindow, text="Turn off", width=15, height=2, command=turn_off,
                       font=("Tahoma", 18, "bold"), relief="solid", bg="black", fg="white")

buttons += [tk.Button(mainWindow, text="Watch video " + str(1), width=12, height=2,
                      command=lambda: replay_video(suspicious_videos[0]),
                      font=("Tahoma", 18, "bold"), relief="solid", bg="black", fg="white")]
buttons += [tk.Button(mainWindow, text="Watch video " + str(2), width=12, height=2,
                      command=lambda: replay_video(suspicious_videos[1]),
                      font=("Tahoma", 18, "bold"), relief="solid", bg="black", fg="white")]
buttons += [tk.Button(mainWindow, text="Watch video " + str(3), width=12, height=2,
                      command=lambda: replay_video(suspicious_videos[2]),
                      font=("Tahoma", 18, "bold"), relief="solid", bg="black", fg="white")]
buttons += [tk.Button(mainWindow, text="Watch video " + str(4), width=12, height=2,
                      command=lambda: replay_video(suspicious_videos[3]),
                      font=("Tahoma", 18, "bold"), relief="solid", bg="black", fg="white")]
mainWindow.mainloop()
