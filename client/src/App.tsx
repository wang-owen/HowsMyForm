const UploadForm = () => {
    return (
        <div
            id="root"
            className="flex flex-col justify-center items-center h-screen space-y-10"
        >
            <h1 className="text-5xl font-bold">How's My Form?</h1>
            <p className="text-2xl text-center">
                Upload a video of your workout, and we'll analyze your form to
                help you improve!
            </p>
            <form
                action="/upload"
                method="POST"
                encType="multipart/form-data"
                className="flex flex-col items-center space-y-6"
            >
                <label htmlFor="video-upload" className="text-xl font-medium">
                    Upload your workout video:
                </label>
                <input
                    type="file"
                    id="video-upload"
                    name="video-upload"
                    accept="video/*"
                    required
                    className="border border-gray-300 p-4 text-lg"
                />
                <button
                    type="submit"
                    className="bg-blue-500 text-white py-3 px-6 text-lg rounded hover:bg-blue-600"
                >
                    Submit
                </button>
            </form>
        </div>
    );
};

export default UploadForm;
