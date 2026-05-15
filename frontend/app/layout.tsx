import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from '@clerk/nextjs';
import ColdStartBanner from "@/components/ColdStartBanner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "CyberGuardAI One",
    description: "Your Personal Digital Bodyguard",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <ClerkProvider>
            <html lang="en">
                <body className={inter.className}>
                    <ColdStartBanner />
                    {children}
                </body>
            </html>
        </ClerkProvider>
    );
}
