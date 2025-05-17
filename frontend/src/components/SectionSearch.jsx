import { useState } from "react";
import React from "react";
export default function SectionSearch() {
  const [q, setQ] = useState("");
  const [page, setPage] = useState(0);
  const [resp, setResp] = useState(null);
  const pageSize = 10;
  const BASE_URL = "https://legendary-halibut-pwwxp7xvwxwf995-8000.app.github.dev";

  const runSearch = async (pageIndex = 0) => {
    if (q.trim().length < 3) return;
  
    const params = new URLSearchParams({
      q,
      offset: pageIndex * pageSize,
      limit: pageSize,
    });
  
    const searchUrl = `${BASE_URL}/api/search?${params.toString()}`;
    console.log("🔍 Searching at:", searchUrl);
  
    const r = await fetch(searchUrl);
    if (!r.ok) throw new Error(`Search failed (${r.status})`);
    const data = await r.json();
  
    setPage(pageIndex);
    setResp(data);
  };

  const maxPage = resp ? Math.floor((resp.total - 1) / pageSize) : 0;

  return (
    <div className="space-y-6">
      {/* search bar */}
      <div className="flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && runSearch(0)}
          placeholder="Search section titles…"
          className="border border-gray-300 rounded px-3 py-2 flex-grow focus:ring focus:ring-blue-200"
        />
        <button
          onClick={() => runSearch(0)}
          className="bg-blue-600 text-white px-4 rounded hover:bg-blue-700"
        >
          Search
        </button>
      </div>

      {/* results */}
      {resp && (
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Showing {resp.offset + 1}‑
            {Math.min(resp.offset + resp.results.length, resp.total)} of&nbsp;
            {resp.total} results
          </p>

          <ul className="space-y-2">
            {resp.results.map((s) => (
              <li
                key={s.title + s.identifier}
                className="bg-white shadow-sm rounded p-3 border border-gray-200"
              >
                <details>
                  <summary className="cursor-pointer">
                    <span className="font-medium">
                      Title&nbsp;
                      <a
                        href={`https://www.ecfr.gov/current/title-${s.title}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        {s.title}
                      </a>
                    </span>
                    &nbsp;– §{s.identifier}&nbsp;– {s.label}
                  </summary>

                  <pre className="bg-gray-50 p-2 text-xs rounded mt-2 overflow-auto">
                    {JSON.stringify(s, null, 2)}
                  </pre>
                </details>
              </li>
            ))}
          </ul>

          {/* pagination */}
          <div className="flex items-center justify-between">
            <button
              className="px-3 py-1 border rounded disabled:opacity-40"
              onClick={() => runSearch(page - 1)}
              disabled={page === 0}
            >
              ‹ Prev
            </button>
            <span className="text-sm">
              Page {page + 1} / {maxPage + 1}
            </span>
            <button
              className="px-3 py-1 border rounded disabled:opacity-40"
              onClick={() => runSearch(page + 1)}
              disabled={page >= maxPage}
            >
              Next ›
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
