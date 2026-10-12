document.addEventListener("DOMContentLoaded", () => {
  const navToggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".nav-links");
  if (navToggle && nav) {
    navToggle.addEventListener("click", () => {
      const opened = nav.classList.toggle("opened");
      navToggle.setAttribute("aria-expanded", String(opened));
    });
    nav.querySelectorAll("a").forEach(a => a.addEventListener("click", () => nav.classList.remove("opened")));
  }

  const qtyInputs = [...document.querySelectorAll(".qty-control input")];
  const summary = document.getElementById("order-summary");
  const totalEl = document.getElementById("order-total");
  const money = n => "₹" + n.toLocaleString("en-IN");
  function updateOrder() {
    let total = 0, chosen = [];
    qtyInputs.forEach(input => {
      const qty = Math.max(0, Number.parseInt(input.value || "0", 10) || 0);
      const price = Number(input.dataset.price || 0);
      if (qty > 0) {
        const card = input.closest(".menu-card");
        const name = card.querySelector("h3").textContent;
        chosen.push(`${name} × ${qty}`);
        total += qty * price;
      }
    });
    summary.textContent = chosen.length ? chosen.join(" · ") : "Select items from the menu to get started.";
    totalEl.textContent = money(total);
  }
  qtyInputs.forEach(input => input.addEventListener("input", updateOrder));
  updateOrder();

  const bookingType = document.getElementById("booking-type");
  const roomFields = document.getElementById("room-fields");
  const tableFields = document.getElementById("table-fields");
  const checkin = document.getElementById("checkin");
  const checkout = document.getElementById("checkout");
  const tableDate = document.getElementById("table-date");
  const tableTime = document.getElementById("table-time");
  const today = new Date();
  const localDate = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,"0")}-${String(today.getDate()).padStart(2,"0")}`;
  [checkin, checkout, tableDate].filter(Boolean).forEach(el => el.min = localDate);
  function toggleBookingFields() {
    const isRoom = bookingType.value === "room";
    roomFields.hidden = !isRoom;
    tableFields.hidden = isRoom;
    checkin.required = isRoom;
    checkout.required = isRoom;
  }
  if (bookingType) bookingType.addEventListener("change", toggleBookingFields);
  if (tableDate) tableDate.addEventListener("change", () => {
    checkin.value = tableDate.value;
    if (tableTime) {
      const time = tableTime.value;
      const match = time.match(/(\d{1,2}):00\s*(AM|PM)/i);
      if (match) {
        let hour = Number(match[1]) % 12;
        if (match[2].toUpperCase() === "PM") hour += 12;
        checkin.dataset.tableTime = `${String(hour).padStart(2,"0")}:00`;
      }
    }
  });
  if (tableTime) tableTime.addEventListener("change", () => {
    const hidden = document.querySelector('input[name="table_time"]');
    if (hidden) hidden.value = tableTime.value;
  });
  if (bookingType) toggleBookingFields();
});
