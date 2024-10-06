import { useState, useEffect, useRef } from "react";
import logo from "./assets/logo.png"; // Import the logo image

const App = () => {
    const [file, setFile] = useState(null);
    const [fileName, setFileName] = useState(""); // State for the name of the uploaded file
    const [dragActive, setDragActive] = useState(false);
    const [movement, setMovement] = useState(""); // State for selected movement
    const [isSubmitting, setIsSubmitting] = useState(false); // State for form submission status
    const [isComplete, setIsComplete] = useState(false); // State for submission completion

    const [warningFrames, setWarningFrames] = useState([]); // State for warning frames
    const [videoUrl, setVideoUrl] = useState(""); // State for video URL
    const lastFramePaused = useRef(-1); // State for last frame paused
    const [pauseButton, setPauseButton] = useState("Play");

    // Handles file drop
    const handleDrop = (event: any) => {
        event.preventDefault();
        event.stopPropagation();
        setDragActive(false);

        if (event.dataTransfer.files && event.dataTransfer.files[0]) {
            const selectedFile = event.dataTransfer.files[0];
            setFile(selectedFile); // Capture the dropped file
            setFileName(selectedFile.name); // Store the name of the dropped file
        }
    };

    // Handles drag over event
    const handleDragOver = (event: any) => {
        event.preventDefault();
        event.stopPropagation();
        setDragActive(true);
    };

    // Handles drag leave event
    const handleDragLeave = (event: any) => {
        event.preventDefault();
        event.stopPropagation();
        setDragActive(false);
    };

    // Handles file selection via the file input
    const handleFileChange = (event: any) => {
        if (event.target.files && event.target.files[0]) {
            const selectedFile = event.target.files[0];
            setFile(selectedFile); // Capture the selected file
            setFileName(selectedFile.name); // Store the name of the selected file
        }
    };

    // Handles movement selection
    const handleMovementChange = (event: any) => {
        setMovement(event.target.value); // Capture the selected movement
    };

    // Handles form submission
    const handleSubmit = async (event: any) => {
        event.preventDefault(); // Prevent default form submission

        if (!file) {
            alert("Please upload a video file.");
            return;
        }

        setIsSubmitting(true); // Set submission state to true to display the spinner

        const formData = new FormData();
        formData.append("video-upload", file); // Append file to FormData
        formData.append("movement", movement); // Append selected movement to FormData

        try {
            const response = await fetch("http://127.0.0.1:8000/check-form", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                console.log("Video uploaded successfully!");
                const data = await response.json();
                setWarningFrames(data.warning_frames);
                setVideoUrl(data.url);
                setIsComplete(true);
            } else {
                console.error("Upload failed.");
                setIsComplete(true);
            }
        } catch (error) {
            console.error("Error during upload:", error);
        } finally {
            setIsSubmitting(false); // Set submission state to false
        }
    };

    // Effect to add the event listener for the video after it has been set
    useEffect(() => {
        const videoElement = document.getElementById(
            "pose-video"
        ) as HTMLVideoElement;

        if (videoElement) {
            // Check if the video time has reached or exceeded a warning frame
            const checkWarningFrames = () => {
                const currentTime = videoElement.currentTime;
                for (const warningFrame of warningFrames) {
                    if (
                        warningFrame !== lastFramePaused.current &&
                        currentTime >= warningFrame / 30
                    ) {
                        console.log(warningFrame);
                        videoElement.pause();
                        setPauseButton("Play");
                        lastFramePaused.current = warningFrame;
                    }
                }
            };
            // Add the timeupdate event listener
            videoElement.addEventListener("timeupdate", checkWarningFrames);

            // Cleanup listener on unmount
            return () => {
                videoElement.removeEventListener(
                    "timeupdate",
                    checkWarningFrames
                );
            };
        }
    }, [videoUrl]); // Run this effect when videoUrl changes

    return (
        <div
            id="root"
            className="flex flex-col justify-center items-center h-screen space-y-10 bg-gradient-to-r from-blue-300 via-blue-400 to-blue-500 font-sans text-white"
        >
            <div className="absolute top-4 left-4">
                <img src={logo} alt="Logo" className="h-32 w-auto" />
            </div>
            <h1 className="text-7xl font-extrabold text-center">
                How's My Form?
            </h1>
            {/* Check if analysis is complete */}
            {isComplete ? (
                <div className="flex flex-col items-center space-y-4">
                    <p className="text-2xl">
                        Analysis complete! You were using poor form in the
                        following timestamps:
                    </p>
                    {videoUrl && (
                        <div>
                            <div className="flex flex-col gap-8 items-center">
                                <ul className="flex gap-4">
                                    {warningFrames.map((frame, index) => (
                                        <li key={index} className="font-bold">
                                            {Math.round((frame / 30) * 100) /
                                                100}
                                            s
                                        </li>
                                    ))}
                                </ul>
                                <video
                                    id="pose-video"
                                    src={videoUrl}
                                    className="border-8 max-h-[700px] rounded-2xl"
                                    autoPlay
                                    muted
                                />
                            </div>
                        </div>
                    )}
                    <div className="flex gap-8">
                        <button
                            onClick={() => {
                                const videoElement = document.getElementById(
                                    "pose-video"
                                ) as HTMLVideoElement;
                                if (videoElement && videoElement.paused) {
                                    videoElement.play();
                                    setPauseButton("Pause");
                                } else {
                                    videoElement.pause();
                                    setPauseButton("Play");
                                }
                            }}
                            className="bg-gradient-to-r from-blue-500 to-blue-700 text-white py-3 px-6 text-lg rounded-lg shadow-lg transition-transform duration-300 hover:scale-105 hover:shadow-xl transform hover:bg-blue-600"
                        >
                            {pauseButton}
                        </button>
                        <button
                            onClick={() => {
                                const videoElement = document.getElementById(
                                    "pose-video"
                                ) as HTMLVideoElement;
                                if (videoElement) {
                                    videoElement.currentTime = 0;
                                    videoElement.pause();
                                    setPauseButton("Play");
                                }
                                lastFramePaused.current = -1;
                            }}
                            className="bg-gradient-to-r from-blue-500 to-blue-700 text-white py-3 px-6 text-lg rounded-lg shadow-lg transition-transform duration-300 hover:scale-105 hover:shadow-xl transform hover:bg-blue-600"
                        >
                            Reset
                        </button>
                    </div>
                </div>
            ) : isSubmitting ? (
                <div className="flex flex-col items-center space-y-4">
                    <div className="w-16 h-16 border-4 border-t-4 border-white rounded-full animate-spin"></div>
                    <p className="text-2xl">Analyzing your video...</p>
                </div>
            ) : (
                <>
                    <p className="text-xl text-center max-w-xl">
                        Upload a video of your workout, and we'll analyze your
                        form to help you improve!
                    </p>
                    <form
                        onSubmit={handleSubmit}
                        className="flex flex-col items-center space-y-6 w-full max-w-md"
                    >
                        {/* Dropdown for movement selection */}
                        <select
                            value={movement}
                            onChange={handleMovementChange}
                            className="bg-white text-gray-800 p-3 rounded-md shadow-md transition duration-200 ease-in-out hover:bg-gray-100"
                            required
                        >
                            <option value="" disabled>
                                Select your movement
                            </option>
                            <option value="bench">Bench Press</option>
                            <option value="squat">Squat</option>
                            <option value="deadlift">Deadlift</option>
                        </select>

                        <div
                            className={`border-4 border-dashed border-white p-10 w-full text-center cursor-pointer rounded-lg transition-transform duration-300 transform hover:scale-105 ${
                                dragActive
                                    ? "bg-white bg-opacity-20"
                                    : "bg-white bg-opacity-10"
                            }`}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                            onClick={() =>
                                document.getElementById("video-upload")?.click()
                            }
                        >
                            {fileName ? (
                                <p className="text-white mt-2 font-semibold">
                                    Uploaded Video: "{fileName}"
                                </p>
                            ) : (
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-20 w-20 mx-auto text-white opacity-80"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        d="M12 16v-8m0 0l-4 4m4-4l4 4M4 16h16"
                                    />
                                </svg>
                            )}
                        </div>
                        <input
                            type="file"
                            id="video-upload"
                            name="video-upload"
                            accept="video/*"
                            className="hidden"
                            onChange={handleFileChange}
                        />
                        <button
                            type="submit"
                            className="bg-gradient-to-r from-blue-500 to-blue-700 text-white py-3 px-6 text-lg rounded-lg shadow-lg transition-transform duration-300 hover:scale-105 hover:shadow-xl transform hover:bg-blue-600"
                        >
                            Submit
                        </button>
                    </form>
                </>
            )}
        </div>
    );
};

export default App;
