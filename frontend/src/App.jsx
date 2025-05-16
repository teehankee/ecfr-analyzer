import { useEffect, useState } from "react";
import SectionSearch from "./components/SectionSearch";
import ReloadButton from "./components/ReloadButton";

export default function App() {
  const [generatedTs, setGeneratedTs] = useState(null);

  // fetch once on mount
  useEffect(() => {
    fetchMetrics();
  }, []);

  async function fetchMetrics() {
    const m = await fetch("/api/metrics").then((r) => r.json());
    setGeneratedTs(m.generated);
  }

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold flex items-center gap-4">
        eCFR Explorer
        <ReloadButton initialTs={generatedTs} onDone={fetchMetrics} />
      </h1>

      <SectionSearch />

      {generatedTs && (
        <p className="text-xs text-gray-600">
          Data snapshot generated{" "}
          {new Date(generatedTs * 1000).toLocaleString()}
        </p>
      )}
    </div>
  );
}
