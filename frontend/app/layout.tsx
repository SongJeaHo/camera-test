import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "camera-test",
  description: "실시간 카메라 인물 분석",
};

const RootLayout = ({ children }: { children: React.ReactNode }) => (
  <html lang="ko">
    <body>{children}</body>
  </html>
);

export default RootLayout;
