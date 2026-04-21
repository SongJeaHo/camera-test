import CameraView from "@/components/CameraView";

const Page = () => (
  <main className="min-h-screen flex flex-col items-center gap-4 p-6">
    <header className="w-full max-w-4xl">
      <h1 className="text-2xl font-semibold">camera-test</h1>
      <p className="text-sm text-gray-400">
        실시간 웹캠 영상에서 사람을 탐지하고 성별·나이를 분석합니다. (Phase 2)
      </p>
    </header>
    <CameraView />
  </main>
);

export default Page;
