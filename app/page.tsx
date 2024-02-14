/**
 * v0 by Vercel.
 * @see https://v0.dev/t/yfi5RP9om8G
 * Documentation: https://v0.dev/docs#integrating-generated-code-into-your-nextjs-app
 */
"use client";
import React, { useState } from "react";
import axios from "axios";
import * as z from "zod";
import { Input } from "@/app/components/ui/input"
import { JSX, SVGProps } from "react"
import { Form, FormControl, FormField, FormItem } from "@/app/components/ui/form";
import { Button } from "@/app/components/ui/button";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";



interface Message {
    role: 'user' | 'bot';
    content: string;
}

const ConversationPage = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const chatForm = useForm({
        resolver: zodResolver(z.object({ message: z.string().min(1, 'Message is required.') })),
    });

    const onChatSubmit = async (data: any) => {
        setIsLoading(true);
        try {
            const response = await axios.post('/api/chat', { message: data.message });
            setMessages([...messages, { role: 'user', content: data.message }, { role: 'bot', content: response.data }]);
        } catch (error) {
            console.error('Error in chat: ', error);
        }
        setIsLoading(false);
        chatForm.reset();
    };

    return (
        <div className="flex h-screen p-4">
            <div className="flex flex-col flex-1">
                <header className="flex items-center justify-between bg-white px-4 py-2 mb-4">
                    <h1 className="text-xl font-semibold">Gemini</h1>
                    <div className="flex items-center space-x-2">
                        <DownloadIcon className="h-6 w-6 text-gray-600" />
                    </div>
                </header>
                <main className="flex-1 overflow-y-auto p-4">
                    {messages.map((message, index) => (
                        <div key={index} className={`mb-4 flex ${message.role === 'user' ? 'items-center' : 'items-start'} space-x-2`}>
                            {message.role === 'user' ? <UserIcon className="mt-1 h-6 w-6 text-blue-500" /> : <StarIcon className="mt-1 h-6 w-6 text-blue-500" />}
                            <p>{message.content}</p>
                        </div>
                    ))}
                </main>
                <footer className="flex items-center justify-between bg-gray-100 px-4 py-2 mt-4">
                    <Form {...chatForm}>
                        <form onSubmit={chatForm.handleSubmit(onChatSubmit)} className="rounded-lg border w-full p-4 px-3 md:px-6 focus-within:shadow-sm grid grid-cols-12 gap-2">
                            <FormField name="message" render={({ field }) => (
                                <FormItem className="col-span-12 lg:col-span-7">
                                    <FormControl className="m-0 p-0">
                                        <Input {...field} className="flex-1 rounded-md border-2 border-gray-300 px-4 py-2" placeholder="Type a message..." type="text" />
                                    </FormControl>
                                </FormItem>
                            )} />
                            <div className="col-span-12 lg:col-span-5 flex justify-end items-center">
                                <Button type="submit">
                                    <SendIcon className="h-5 w-5 text-gray-600" />
                                </Button>
                            </div>
                        </form>
                    </Form>
                </footer>
            </div>
        </div>
    );
};


function DownloadIcon(props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" x2="12" y1="15" y2="3" />
        </svg>
    )
}

function SendIcon(props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="m22 2-7 20-4-9-9-4Z" />
            <path d="M22 2 11 13" />
        </svg>
    )
}


function StarIcon(props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
    )
}


function UserIcon(props: JSX.IntrinsicAttributes & SVGProps<SVGSVGElement>) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 7C13.66 7 15 8.34 15 10C15 11.66 13.66 13 12 13C10.34 13 9 11.66 9 10C9 8.34 10.34 7 12 7ZM12 15C9.33 15 4 16.34 4 19V20H20V19C20 16.34 14.67 15 12 15Z" />
        </svg>
    );
}

export default ConversationPage;
