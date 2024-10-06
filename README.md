## Inspiration
As important as maintaining one's health is, we wanted to create something to help those interested in weightlifting to jump straight into it without fear of injury with an app that detects and warns users of poor form during important compound lifts.

## What it does
Our app analyzes your lifting form using a computer vision pose estimation model, calculates key points within a provided video in where the user exhibits poor form, and gives suggestions based on these key points.

## How we built it
- We used **Ultralytics' YOLOv8** pose estimation model to landmark and track a persons joints
- **Django** alongside the **Django REST framework** were used on the server side to build a **RESTful API**
- **React, TypeScript, and Tailwind CSS** were used to design the client and fetch data from the server
- We used Cloudflare's AI Worker API to access their Llama 3 LLM model to provide Chadbot
- Video files annotated with pose estimation landmarks were uploaded to Cloudflare's **R2 buckets**, which would then be served to the client to display to the user
- Adobe Express was used to generate key images used throughout the site.
- Git was used for version control and collaboration

## Challenges we ran into
We faced challenges in accurately detecting a person's landmarks (joints) and ensuring real-time feedback for users, as well as serving the annotated video result back to the client.

## Accomplishments that we're proud of
We learned and implemented technology of an unfamiliar field (computer vision and machine learning) in a project that builds upon our existing knowledge of full-stack web development.

## What we learned
We learned the importance of refining machine learning models, especially when it comes to pose estimation, where a user's landmarks can vary drastically based on various factors such as camera angle and distance from target.

## What's next for How’sMyForm?
We plan to enhance our community support and integrate personalized workout plans to further assist users in their fitness journeys, such as implementing new algorithms for different lifts (e.g. RDL, bicep curls) as well as determining the camera angle automatically.
