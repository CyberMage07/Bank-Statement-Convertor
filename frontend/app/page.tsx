export default function LandingPage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white p-10">
      <h1 className="text-4xl font-bold">FinDoc AI</h1>
      <p className="mt-4 max-w-2xl text-slate-300">
        Financial Document Intelligence Platform for CAs, auditors, and finance teams.
      </p>
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <section className="rounded-lg bg-slate-900 p-4">Upload financial docs</section>
        <section className="rounded-lg bg-slate-900 p-4">Review AI extraction</section>
        <section className="rounded-lg bg-slate-900 p-4">Export to accounting systems</section>
      </div>
    </main>
  );
}
