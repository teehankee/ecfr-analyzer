import React from "react";
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
    const baseUrl   = "https://legendary-halibut-pwwxp7xvwxwf995-8000.app.github.dev";
    const endpoint  = "/api/metrics";
    const fullUrl   = `${baseUrl}${endpoint}`;
  
    console.log("📡 Fetching metrics from:", fullUrl);
    const m = await fetch(fullUrl).then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    });
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
