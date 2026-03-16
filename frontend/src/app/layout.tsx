import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "🦐 苹果虾资讯 - AI 资讯聚合平台",
  description: "每日自动更新 AI 大模型、行业资讯、国际政治、金融板块最新资讯",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
