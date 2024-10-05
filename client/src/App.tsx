import { useState } from "react";
import logo from "./assets/logo.png"; // Import the logo image

const UploadForm = () => {
    const [file, setFile] = useState(null);
    const [fileName, setFileName] = useState(""); // State for the name of the uploaded file
    const [dragActive, setDragActive] = useState(false);
    const [movement, setMovement] = useState(""); // State for selected movement

    // Handles file drop
    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const selectedFile = e.dataTransfer.files[0];
            setFile(selectedFile); // Capture the dropped file
            setFileName(selectedFile.name); // Store the name of the dropped file
        }
    };

    // Handles drag over event
    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(true);
    };

    // Handles drag leave event
    const handleDragLeave = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
    };

    // Handles file selection via the file input
    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            setFile(selectedFile); // Capture the selected file
            setFileName(selectedFile.name); // Store the name of the selected file
        }
    };

    // Handles movement selection
    const handleMovementChange = (e) => {
        setMovement(e.target.value); // Capture the selected movement
    };

    // Handles form submission
    const handleSubmit = async (e) => {
        e.preventDefault(); // Prevent default form submission

        if (!file) {
            alert("Please upload a video file.");
            return;
        }

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
            } else {
                console.error("Upload failed.");
            }
        } catch (error) {
            console.error("Error during upload:", error);
        }
    };

    return (
        <div
            id="root"
            className="flex flex-col justify-center items-center h-screen space-y-10 bg-gradient-to-r from-blue-300 via-blue-400 to-blue-500 font-sans text-white" // Updated to a lighter blue gradient
        >
            <div className="absolute top-4 left-4">
                <img src={logo} alt="Logo" className="h-32 w-auto" style={{ display: 'block' }} /> {/* Removed any border */}
            </div>
            <h1 className="text-7xl font-extrabold text-center">How's My Form?</h1> {/* No jumping title */}
            <p className="text-xl text-center max-w-xl">
                Upload a video of your workout, and we'll analyze your form to help you improve!
            </p>
            <form onSubmit={handleSubmit} className="flex flex-col items-center space-y-6 w-full max-w-md">
                {/* Dropdown for movement selection */}
                <select
                    value={movement}
                    onChange={handleMovementChange}
                    className="bg-white text-gray-800 p-3 rounded-md shadow-md transition duration-200 ease-in-out hover:bg-gray-100"
                    required
                >
                    <option value="" disabled>Select your movement</option>
                    <option value="bench">Bench Press</option>
                    <option value="squat">Squat</option>
                    <option value="deadlift">Deadlift</option>
                </select>

                <div
                    className={`border-4 border-dashed border-white p-10 w-full text-center cursor-pointer rounded-lg transition-transform duration-300 transform hover:scale-105 ${
                        dragActive ? "bg-white bg-opacity-20" : "bg-white bg-opacity-10"
                    }`}
                    onDragOver={handleDragOver} // Activate drag over event
                    onDragLeave={handleDragLeave} // Activate drag leave event
                    onDrop={handleDrop} // Handle file drop
                    onClick={() => document.getElementById("video-upload").click()} // Click to open file input
                >
                    {/* Conditionally display uploaded video name or upload logo text */}
                    {fileName ? (
                        <p className="text-white mt-2 font-semibold">Uploaded Video: "{fileName}"</p>
                    ) : (
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-20 w-20 mx-auto text-white opacity-80" // Increased icon size
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
                    className="hidden" // Hide the file input field
                    onChange={handleFileChange} // Handle file selection
                />
                <button
                    type="submit"
                    className="bg-gradient-to-r from-blue-500 to-blue-700 text-white py-3 px-6 text-lg rounded-lg shadow-lg transition-transform duration-300 hover:scale-105 hover:shadow-xl transform hover:bg-blue-600"
                >
                    Submit
                </button>
            </form>
        </div>
    );
};

export default UploadForm;