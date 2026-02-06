const form = document.getElementById("uploadForm");
const resumeInput = document.getElementById("resume");
const jdInput = document.getElementById("jd");
const resultEl = document.getElementById("result");
const scheduleSection = document.getElementById("scheduleSection");
const scheduleBtn = document.getElementById("scheduleBtn");
const shortlistEl = document.getElementById("shortlist");

let shortlist = [];

async function analyze() {
  if (!resumeInput.files.length) {
    resultEl.innerText = "Please choose one or more resume files.";
    return;
  }
  if (!jdInput.value.trim()) {
    resultEl.innerText = "Please paste a job description.";
    return;
  }

  const formData = new FormData();
  for (const file of resumeInput.files) {
    formData.append("resumes", file);
  }
  formData.append("jd", jdInput.value);

  resultEl.innerText = "Analyzing resume...";
  const res = await fetch("http://localhost:8000/analyze-batch", {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  shortlist = [];
  scheduleSection.style.display = "none";
  shortlistEl.innerHTML = "";

  const results = data?.results || [];
  if (!results.length) {
    resultEl.innerText = "Analysis failed. Please try again.";
    return;
  }

  let rejectedCount = 0;
  const rejectedDetails = [];
  for (const item of results) {
    const analysis = item?.agent_response?.analysis;
    const candidateEmail = item?.agent_response?.candidate_email;
    const shouldSchedule = item?.agent_response?.should_schedule;
    const candidateName = analysis?.candidate_name || item?.filename || "Candidate";
    if (shouldSchedule && candidateEmail && analysis) {
      shortlist.push({
        name: candidateName,
        email: candidateEmail,
        score: analysis.score
      });
    } else {
      rejectedCount += 1;
      if (analysis) {
        rejectedDetails.push(`${candidateName} (Score: ${analysis.score})`);
      } else {
        rejectedDetails.push(`${candidateName} (No analysis)`);
      }
    }
  }

  if (!shortlist.length) {
    resultEl.innerText =
      `No shortlisted candidates.\nRejected: ${rejectedCount}\n` +
      rejectedDetails.join("\n");
    return;
  }

  resultEl.innerText =
    `Shortlisted: ${shortlist.length}\nRejected: ${rejectedCount}\n\n` +
    (rejectedDetails.length ? `Rejected list:\n${rejectedDetails.join("\n")}\n\n` : "") +
    "Pick date/time for each selected candidate and click Schedule.";

  for (const c of shortlist) {
    const row = document.createElement("div");
    row.className = "shortlist-row";
    row.innerHTML = `
      <label class="shortlist-check">
        <input type="checkbox" checked data-email="${c.email}" />
        <span>${c.name}</span>
      </label>
      <span class="shortlist-meta">${c.email}</span>
      <span class="shortlist-meta">Score: ${c.score}</span>
      <input type="datetime-local" class="shortlist-dt" data-email="${c.email}" />
    `;
    shortlistEl.appendChild(row);
  }
  scheduleSection.style.display = "block";
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  await analyze();
});

// Auto-run when a file is selected (if JD is already filled)
resumeInput.addEventListener("change", async () => {
  if (jdInput.value.trim()) {
    await analyze();
  } else {
    resultEl.innerText = "Now paste the job description and click Analyze.";
  }
});

scheduleBtn.addEventListener("click", async (e) => {
  e.preventDefault();
  if (!shortlist.length) {
    resultEl.innerText = "Analyze resumes first.";
    return;
  }

  const checked = Array.from(
    shortlistEl.querySelectorAll("input[type='checkbox']:checked")
  );
  if (!checked.length) {
    resultEl.innerText = "Select at least one candidate.";
    return;
  }

  const dtInputs = shortlistEl.querySelectorAll(".shortlist-dt");
  const dtMap = {};
  dtInputs.forEach((el) => {
    dtMap[el.dataset.email] = el.value;
  });

  const toSchedule = [];
  for (const box of checked) {
    const email = box.dataset.email;
    const candidate = shortlist.find((c) => c.email === email);
    const dt = dtMap[email];
    if (!dt) {
      resultEl.innerText = `Please select date/time for ${candidate.name}.`;
      return;
    }
    const selected = new Date(dt);
    if (Number.isNaN(selected.getTime()) || selected <= new Date()) {
      resultEl.innerText = `Invalid date/time for ${candidate.name}.`;
      return;
    }
    toSchedule.push({ ...candidate, datetime: dt });
  }

  resultEl.innerText = "Scheduling interview...";
  const results = [];
  for (const c of toSchedule) {
    const formData = new FormData();
    formData.append("candidate_name", c.name);
    formData.append("candidate_email", c.email);
    formData.append("interview_datetime", c.datetime);
    formData.append("timezone", "Asia/Kolkata");

    const res = await fetch("http://localhost:8000/schedule", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    results.push({ candidate: c.name, response: data });
  }

  let message = "Scheduling complete.\n";
  for (const r of results) {
    if (r.response?.schedule) {
      const s = r.response.schedule;
      message += `\n${r.candidate}: Scheduled at ${s.interview_date} ${s.interview_time} (IST)\nMeet: ${s.meet_link}\n`;
    } else {
      message += `\n${r.candidate}: Scheduling failed.`;
    }
  }
  resultEl.innerText = message;
});
