import { useState, useEffect, useRef } from "react";

const Chatbot = () => {
    const [messages, setMessages] = useState<
        { role: string; content: string }[]
    >([
        {
            content:
                "Hello! I'm Chadbot, your friendly assistant for anything fitness and health related.",
            role: "system",
        },
    ]);
    const [input, setInput] = useState("");
    const messagesEndRef = useRef<HTMLDivElement>(null); // Reference to the end of the message list
    const [loading, setLoading] = useState(false);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom(); // Scroll to bottom whenever messages change
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        // Add the user's message to the chat
        setMessages([...messages, { role: "user", content: input }]);
        setInput("");
        setLoading(true);

        try {
            const response = await fetch("http://127.0.0.1:8000/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ messages: messages }),
            });

            const result = await response.json();
            const botResponse = result.result.response;

            setMessages((prevMessages) => [
                ...prevMessages,
                { role: "system", content: botResponse },
            ]);
        } catch (error) {
            console.error(
                "Error communicating with the Llama 3 Worker:",
                error
            );
            setMessages((prevMessages) => [
                ...prevMessages,
                { role: "system", content: "Sorry, there was an error." },
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="absolute bottom-56 right-10 w-80 h-96 bg-white border border-gray-300 rounded-lg shadow-lg flex flex-col text-black">
            <div className="flex-1 p-3 overflow-y-auto bg-gray-50">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`mb-2 p-2 max-w-[75%] rounded-lg ${
                            msg.role === "user"
                                ? "bg-blue-200 self-end"
                                : "bg-orange-200 self-start"
                        }`}
                    >
                        {msg.content}
                    </div>
                ))}
                <div ref={messagesEndRef} /> {/* Empty div to scroll to */}
            </div>
            <div className="border-t p-3 flex">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
                    className="flex-1 border border-gray-300 rounded-lg p-2 focus:outline-none"
                    placeholder="Type a message..."
                />
                <button
                    onClick={handleSend}
                    disabled={loading}
                    className="bg-gradient-to-r from-blue-500 to-blue-700 text-white py-3 px-3 rounded-lg shadow-lg transition-transform duration-300 hover:scale-105 hover:shadow-xl transform hover:bg-blue-600 ml-2"
                >
                    {loading ? "..." : "Send"}
                </button>
            </div>
        </div>
    );
};

export default Chatbot;
