import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WebSketch",
  description: "Wireframe editor application",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
