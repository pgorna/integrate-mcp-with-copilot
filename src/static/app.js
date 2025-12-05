document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const messageDiv = document.getElementById("message");
  let calendar = null;
  let activitiesData = {};

  // View switcher
  const listViewBtn = document.getElementById("list-view-btn");
  const calendarViewBtn = document.getElementById("calendar-view-btn");
  const listView = document.getElementById("list-view");
  const calendarView = document.getElementById("calendar-view");

  listViewBtn.addEventListener("click", () => {
    listView.classList.add("active");
    calendarView.classList.remove("active");
    listViewBtn.classList.add("active");
    calendarViewBtn.classList.remove("active");
  });

  calendarViewBtn.addEventListener("click", () => {
    calendarView.classList.add("active");
    listView.classList.remove("active");
    calendarViewBtn.classList.add("active");
    listViewBtn.classList.remove("active");
    
    // Initialize calendar if not already done
    if (!calendar) {
      initializeCalendar();
    }
  });

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      activitiesData = activities;

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activity filter dropdown
      populateActivityFilter(activities);

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft =
          details.max_participants - details.participants.length;

        // Create participants HTML with delete icons instead of bullet points
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
          <button class="register-btn" data-activity="${name}">Register Student</button>
        `;

        activitiesList.appendChild(activityCard);
      });

      // Add event listeners to delete buttons
      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });

      // Add event listeners to register buttons
      document.querySelectorAll(".register-btn").forEach((button) => {
        button.addEventListener("click", handleRegister);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle register functionality
  async function handleRegister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");

    const email = prompt("Enter student email:", "");
    
    if (!email) {
      return; // User cancelled or entered empty email
    }

    // Email validation with regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      showMessage("Please enter a valid email address", "error");
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  }

  // Handle unregister functionality
  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to unregister. Please try again.", "error");
      console.error("Error unregistering:", error);
    }
  }

  // Helper function to show messages
  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    // Hide message after 5 seconds
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  // Populate activity filter dropdown
  function populateActivityFilter(activities) {
    const activityFilter = document.getElementById("activity-filter");
    activityFilter.innerHTML = '<option value="">All Activities</option>';
    
    Object.keys(activities).forEach(activityName => {
      const option = document.createElement("option");
      option.value = activityName;
      option.textContent = activityName;
      activityFilter.appendChild(option);
    });
  }

  // Initialize FullCalendar
  function initializeCalendar() {
    const calendarEl = document.getElementById("calendar-container");
    
    calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: "dayGridMonth",
      headerToolbar: {
        left: "prev,next today",
        center: "title",
        right: "dayGridMonth,timeGridWeek,timeGridDay"
      },
      events: fetchCalendarEvents,
      eventClick: handleEventClick,
      height: "auto",
      eventTimeFormat: {
        hour: '2-digit',
        minute: '2-digit',
        meridiem: 'short'
      }
    });
    
    calendar.render();
    loadUpcomingEvents();
  }

  // Fetch calendar events
  async function fetchCalendarEvents(info, successCallback, failureCallback) {
    try {
      const activityFilter = document.getElementById("activity-filter").value;
      const studentFilter = document.getElementById("student-filter").value;
      
      let url = "/calendar/events";
      const params = new URLSearchParams();
      
      if (info.start) {
        params.append("start", info.start.toISOString());
      }
      if (info.end) {
        params.append("end", info.end.toISOString());
      }
      if (activityFilter) {
        params.append("activity", activityFilter);
      }
      if (studentFilter) {
        params.append("email", studentFilter);
      }
      
      if (params.toString()) {
        url += "?" + params.toString();
      }
      
      const response = await fetch(url);
      const data = await response.json();
      
      // Transform events to FullCalendar format
      const events = data.events.map(event => ({
        id: event.id,
        title: event.title,
        start: event.start,
        end: event.end,
        backgroundColor: event.color,
        borderColor: event.color,
        extendedProps: {
          activity_name: event.activity_name,
          description: event.description,
          room: event.room,
          is_cancelled: event.is_cancelled
        }
      }));
      
      successCallback(events);
    } catch (error) {
      console.error("Error fetching calendar events:", error);
      failureCallback(error);
    }
  }

  // Handle event click
  function handleEventClick(info) {
    const event = info.event;
    const modal = document.getElementById("event-modal");
    const modalTitle = document.getElementById("modal-event-title");
    const modalDetails = document.getElementById("modal-event-details");
    
    modalTitle.textContent = event.title;
    
    const startDate = new Date(event.start);
    const endDate = new Date(event.end);
    
    modalDetails.innerHTML = `
      <p><strong>Activity:</strong> ${event.extendedProps.activity_name}</p>
      <p><strong>Start:</strong> ${startDate.toLocaleString()}</p>
      <p><strong>End:</strong> ${endDate.toLocaleString()}</p>
      ${event.extendedProps.room ? `<p><strong>Room:</strong> ${event.extendedProps.room}</p>` : ''}
      ${event.extendedProps.description ? `<p><strong>Description:</strong> ${event.extendedProps.description}</p>` : ''}
      ${event.extendedProps.is_cancelled ? `<p style="color: red;"><strong>Status:</strong> CANCELLED</p>` : ''}
    `;
    
    modal.classList.remove("hidden");
  }

  // Close modal
  document.querySelector(".modal-close").addEventListener("click", () => {
    document.getElementById("event-modal").classList.add("hidden");
  });

  // Close modal on outside click
  document.getElementById("event-modal").addEventListener("click", (e) => {
    if (e.target.id === "event-modal") {
      e.target.classList.add("hidden");
    }
  });

  // Apply filters
  document.getElementById("apply-filters-btn").addEventListener("click", () => {
    if (calendar) {
      calendar.refetchEvents();
      loadUpcomingEvents();
    }
  });

  // Clear filters
  document.getElementById("clear-filters-btn").addEventListener("click", () => {
    document.getElementById("activity-filter").value = "";
    document.getElementById("student-filter").value = "";
    if (calendar) {
      calendar.refetchEvents();
      loadUpcomingEvents();
    }
  });

  // Export calendar
  document.getElementById("export-calendar-btn").addEventListener("click", async () => {
    try {
      const activityFilter = document.getElementById("activity-filter").value;
      const studentFilter = document.getElementById("student-filter").value;
      
      let url = "/calendar/export";
      const params = new URLSearchParams();
      
      if (activityFilter) {
        params.append("activity", activityFilter);
      }
      if (studentFilter) {
        params.append("email", studentFilter);
      }
      
      if (params.toString()) {
        url += "?" + params.toString();
      }
      
      window.open(url, "_blank");
      showMessage("Calendar exported successfully!", "success");
    } catch (error) {
      showMessage("Failed to export calendar", "error");
      console.error("Error exporting calendar:", error);
    }
  });

  // Load upcoming events
  async function loadUpcomingEvents() {
    try {
      const activityFilter = document.getElementById("activity-filter").value;
      const studentFilter = document.getElementById("student-filter").value;
      
      const now = new Date();
      const twoWeeksFromNow = new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000);
      
      let url = "/calendar/events";
      const params = new URLSearchParams({
        start: now.toISOString(),
        end: twoWeeksFromNow.toISOString()
      });
      
      if (activityFilter) {
        params.append("activity", activityFilter);
      }
      if (studentFilter) {
        params.append("email", studentFilter);
      }
      
      url += "?" + params.toString();
      
      const response = await fetch(url);
      const data = await response.json();
      
      const upcomingList = document.getElementById("upcoming-events-list");
      
      if (data.events.length === 0) {
        upcomingList.innerHTML = "<p>No upcoming events in the next 2 weeks.</p>";
        return;
      }
      
      // Sort by start date
      const sortedEvents = data.events.sort((a, b) => 
        new Date(a.start) - new Date(b.start)
      ).slice(0, 5); // Show only first 5
      
      upcomingList.innerHTML = sortedEvents.map(event => {
        const startDate = new Date(event.start);
        return `
          <div class="upcoming-event-item">
            <h5>${event.title}</h5>
            <p>📅 ${startDate.toLocaleDateString()} at ${startDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
            <p>📍 ${event.room || 'Location TBD'}</p>
          </div>
        `;
      }).join('');
    } catch (error) {
      console.error("Error loading upcoming events:", error);
      document.getElementById("upcoming-events-list").innerHTML = 
        "<p>Failed to load upcoming events.</p>";
    }
  }

  // Initialize app
  fetchActivities();
  
  // Refresh upcoming events every 5 minutes
  setInterval(loadUpcomingEvents, 5 * 60 * 1000);
});
