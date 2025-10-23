const header = document.querySelector('.calendar h3');
const dates = document.querySelector('.dates');
const navs = document.querySelectorAll('#prev, #next');

const months = [
  'January','February','March','April','May','June',
  'July','August','September','October','November','December'
];

let date = new Date();
let month = date.getMonth();
let year = date.getFullYear();

function renderCalendar() {
  const start = new Date(year, month, 1).getDay();
  const endDate = new Date(year, month + 1, 0).getDate();
  const end = new Date(year, month, endDate).getDay();
  const endDatePrev = new Date(year, month, 0).getDate();

  let datesHtml = '';

  for (let i = start; i > 0; i--) {
    datesHtml += `<li class='inactive'>${endDatePrev - i + 1}</li>`;
  }

  for (let i = 1; i <= endDate; i++) {
    let className =
      i === date.getDate() &&
      month === new Date().getMonth() &&
      year === new Date().getFullYear()
        ? ' class="today"'
        : '';
    datesHtml += `<li${className}>${i}</li>`;
  }

  for (let i = end; i < 6; i++) {
    datesHtml += `<li class="inactive">${i - end + 1}</li>`;
  }

  dates.innerHTML = datesHtml;
  header.textContent = `${months[month]} ${year}`;
}

navs.forEach(nav => {
  nav.addEventListener('click', e => {
    const btnId = e.target.id;
    if (btnId === 'prev' && month === 0) {
      year--;
      month = 11;
    } else if (btnId === 'next' && month === 11) {
      year++;
      month = 0;
    } else {
      month = btnId === 'next' ? month + 1 : month - 1;
    }

    date = new Date(year, month, new Date().getDate());
    renderCalendar();
  });
});

renderCalendar();

const weekDays = document.querySelector('.week-days');
const container = document.querySelector('#timetable-container');
const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

// ---- HIỂN THỊ TUẦN HIỆN TẠI ----
function renderCurrentWeek() {
  const today = new Date();
  const startOfWeek = new Date(today);
  startOfWeek.setDate(today.getDate() - today.getDay()); // về Chủ nhật

  let html = '';
  for (let i = 0; i < 7; i++) {
    const current = new Date(startOfWeek);
    current.setDate(startOfWeek.getDate() + i);

    const isToday =
      current.toDateString() === today.toDateString() ? ' class="today"' : '';

    html += `<li${isToday}><span style="font-size: 24px">${dayNames[i]}</span><br>${current.getDate()}</li>`;
  }

  weekDays.innerHTML = html;
}


// Gọi khi trang load
renderCurrentWeek();
