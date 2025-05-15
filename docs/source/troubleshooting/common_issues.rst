=============
Common Issues
=============

This document provides solutions for common issues that may occur when using or developing the BookingApp system.

Installation Issues
-------------------

**Issue**: Missing dependencies when installing requirements

**Solution**:
   
.. code-block:: bash

   # Make sure pip is up to date
   pip install --upgrade pip
   
   # Install dependencies one by one to identify problematic packages
   pip install fastapi
   pip install aiosqlite
   # Continue with other packages...

**Issue**: "No module named 'fastapi'" error when running the application

**Solution**:
   
Ensure that you've activated the virtual environment and installed all dependencies:

.. code-block:: bash

   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirement.txt

**Issue**: Permission issues when running the application

**Solution**:
   
Check file permissions and ensure the user has write access to the application directory:

.. code-block:: bash

   # On Linux/Mac
   chmod -R 755 /path/to/BookingApp
   
   # Ensure the database directory is writable
   chmod 777 /path/to/BookingApp/database.db

Database Issues
---------------

**Issue**: Database file not found or permission denied

**Solution**:

1. Check that the database file exists:

   .. code-block:: bash

      ls -la database.db

2. Ensure the file has the correct permissions:

   .. code-block:: bash

      chmod 666 database.db

3. Check for database lock files:

   .. code-block:: bash

      ls -la database.db*
      # If lock files exist, you may need to delete them
      rm database.db-shm database.db-wal

**Issue**: Database schema errors

**Solution**:

1. Rename or delete the existing database to recreate it:

   .. code-block:: bash

      mv database.db database.db.bak

2. Manually check the SQL schema:

   .. code-block:: bash

      sqlite3 database.db.bak .schema

3. Compare the schema with create.sql to identify discrepancies

**Issue**: Data corruption

**Solution**:

1. Create a backup of the corrupt database:

   .. code-block:: bash

      cp database.db database.db.corrupt

2. Use SQLite's integrity check:

   .. code-block:: bash

      sqlite3 database.db "PRAGMA integrity_check;"

3. If the database is severely corrupted, restore from a backup or recreate it from scratch

**Issue**: "SQL constraint failed" errors

**Solution**:

1. Check the error message for details about which constraint failed
2. Verify that the data being inserted or updated meets all constraints
3. If necessary, modify the schema to adjust constraints:

   .. code-block:: sql

      -- Example: Modify a constraint
      ALTER TABLE Room RENAME TO Room_old;
      CREATE TABLE Room (
          -- New schema with modified constraints
      );
      INSERT INTO Room SELECT * FROM Room_old;
      DROP TABLE Room_old;

Authentication Issues
---------------------

**Issue**: "Invalid token" errors

**Solution**:

1. Clear browser localStorage to reset tokens:

   .. code-block:: javascript

      // In browser console
      localStorage.clear();

2. Check if the Authentication table has the token:

   .. code-block:: sql

      SELECT * FROM Authentication WHERE token = 'your-token';

3. Ensure token expiration is not being enforced unintentionally

**Issue**: Login failures despite correct credentials

**Solution**:

1. Check if the user exists:

   .. code-block:: sql

      SELECT * FROM User WHERE username = 'user@example.com';

2. Verify that the bcrypt hash is correctly formatted:

   .. code-block:: sql

      SELECT password FROM User WHERE username = 'user@example.com';
      -- Should start with $2b$ for bcrypt

3. Reset the password manually if needed:

   .. code-block:: sql

      -- Replace with a properly hashed password
      UPDATE User SET password = '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m' WHERE username = 'user@example.com';

**Issue**: "Too many failed attempts" error

**Solution**:

1. The application has a rate-limiting mechanism for failed login attempts
2. Wait a few minutes before trying again
3. If necessary, reset the failed attempts counter in the code:

   .. code-block:: python

      # In account.py
      account_manager.reset_failed_attempts(username)

Booking Issues
--------------

**Issue**: "Room already booked" error despite availability

**Solution**:

1. Check for overlapping bookings:

   .. code-block:: sql

      SELECT * FROM Booking WHERE room_id = ? AND start_time <= ? AND (start_time + duration * 3600) > ?;

2. Verify that the time conversion is working correctly:

   .. code-block:: javascript

      // Browser console debugging
      const date = new Date(timestamp * 1000);
      console.log(date.toISOString());

3. Check for timezone issues between client and server

**Issue**: Bookings not appearing in the calendar

**Solution**:

1. Verify that the bookings exist in the database:

   .. code-block:: sql

      SELECT * FROM Booking WHERE room_id = ?;

2. Check that the date filter is correctly applied:

   .. code-block:: javascript

      console.log("Selected date:", selectedDate);
      console.log("Timestamp:", Math.floor(selectedDate.getTime() / 1000));

3. Clear browser cache and reload the page

**Issue**: Unable to cancel or edit bookings

**Solution**:

1. Check if the booking exists:

   .. code-block:: sql

      SELECT * FROM Booking WHERE booking_id = ?;

2. Verify that the user has permission to modify the booking:

   .. code-block:: sql

      SELECT * FROM User_Booking WHERE booking_id = ? AND user_id = ?;

3. Check if the booking is in the past (past bookings cannot be modified):

   .. code-block:: javascript

      const bookingTime = new Date(booking.time * 1000);
      const now = new Date();
      if (bookingTime < now) {
          console.log("Booking is in the past");
      }

Email Notification Issues
-------------------------

**Issue**: Email notifications not being sent

**Solution**:

1. Check SMTP credentials in the .env file:

   .. code-block:: bash

      # .env file
      smtp_username = "your_email@gmail.com"
      smtp_password = "your_app_password"

2. Verify that Gmail's "Less secure app access" is enabled or that you're using an app password

3. Check for network issues or firewall restrictions that might block SMTP traffic

4. Add debug logging to the notification system:

   .. code-block:: python

      def send_email(self, recipient_email: str, subject: str, body: str):
          print(f"Attempting to send email to {recipient_email} with subject: {subject}")
          try:
              # ... existing code ...
              print(f"Email sent successfully to {recipient_email}")
          except Exception as e:
              print(f"Failed to send email: {e}")
              # Log the error for debugging
              import traceback
              traceback.print_exc()

**Issue**: HTML email formatting issues

**Solution**:

1. Check the HTML structure in the email templates
2. Test emails with different email clients to identify client-specific issues
3. Simplify the HTML to use more widely supported elements and styles
4. Add plain text alternatives to HTML emails:

   .. code-block:: python

      from email.mime.multipart import MIMEMultipart
      from email.mime.text import MIMEText
      
      # Create multipart message
      msg = MIMEMultipart("alternative")
      
      # Create plain text version
      text_part = MIMEText("Plain text version of the email", "plain")
      
      # Create HTML version
      html_part = MIMEText(html_body, "html")
      
      # Attach both parts
      msg.attach(text_part)
      msg.attach(html_part)

Frontend Issues
---------------

**Issue**: JavaScript console errors

**Solution**:

1. Check the browser console for specific error messages:

   .. code-block:: javascript

      // Example error handling
      try {
          // Code that might cause an error
          const response = await fetch('/api/endpoint');
          const data = await response.json();
      } catch (error) {
          console.error("Detailed error:", error);
          // Handle the error appropriately
      }

2. Verify that all required JavaScript files are being loaded correctly:

   .. code-block:: html

      <!-- Check HTML for correct script tags -->
      <script type="module" src="/your-script.js"></script>

3. Check for JavaScript compatibility issues with older browsers:

   .. code-block:: javascript

      // Use feature detection
      if (typeof Promise !== 'undefined' && Promise.toString().indexOf('[native code]') !== -1) {
          // Browser supports Promises
      } else {
          // Fallback for browsers without Promise support
      }

**Issue**: CSS styles not applying correctly

**Solution**:

1. Inspect elements to see if CSS classes are being applied:

   .. code-block:: html

      <!-- Use browser developer tools to inspect elements -->
      <div class="expected-class"></div>

2. Check for CSS specificity issues or conflicting styles:

   .. code-block:: css

      /* Use more specific selectors if needed */
      body .booking-item .btn {
          background-color: var(--accent-color);
      }

3. Verify that the CSS files are being loaded in the correct order

**Issue**: Form submission not working

**Solution**:

1. Check that event listeners are properly attached:

   .. code-block:: javascript

      document.addEventListener('DOMContentLoaded', () => {
          const form = document.getElementById('form-id');
          console.log('Form element found:', form);
          
          if (form) {
              form.addEventListener('submit', (e) => {
                  console.log('Form submitted');
                  // Rest of submission logic
              });
          } else {
              console.error('Form element not found!');
          }
      });

2. Validate that form inputs have the correct names and IDs:

   .. code-block:: html

      <input type="text" id="username" name="username">

3. Check network requests in the browser developer tools to see if the form data is being sent correctly

Performance Issues
------------------

**Issue**: Slow page loading times

**Solution**:

1. Minimize the number of API requests:

   .. code-block:: javascript

      // Batch related requests together
      async function loadAllData() {
          const [roomsResponse, bookingsResponse] = await Promise.all([
              fetch('/api/rooms'),
              fetch('/api/bookings')
          ]);
          
          const rooms = await roomsResponse.json();
          const bookings = await bookingsResponse.json();
          
          // Process the data
      }

2. Implement pagination for large data sets:

   .. code-block:: javascript

      async function loadBookings(page = 1, pageSize = 10) {
          const response = await fetch(`/api/bookings?page=${page}&pageSize=${pageSize}`);
          const data = await response.json();
          
          // Process the results
          
          // Add pagination controls
          if (data.hasMore) {
              // Show "Load more" button
          }
      }

3. Use caching for frequently accessed data:

   .. code-block:: javascript

      // Simple cache implementation
      const cache = new Map();
      
      async function fetchWithCache(url, ttlMinutes = 5) {
          const now = Date.now();
          
          if (cache.has(url)) {
              const {data, timestamp} = cache.get(url);
              const age = (now - timestamp) / (1000 * 60); // age in minutes
              
              if (age < ttlMinutes) {
                  console.log(`Using cached data for ${url}`);
                  return data;
              }
          }
          
          console.log(`Fetching fresh data for ${url}`);
          const response = await fetch(url);
          const data = await response.json();
          
          cache.set(url, {data, timestamp: now});
          return data;
      }

**Issue**: Room calendar becomes slow with many rooms and time slots

**Solution**:

1. Implement lazy loading for the room calendar:

   .. code-block:: javascript

      // Load rooms in batches
      function loadVisibleRooms() {
          const visibleStart = Math.floor(scrollPosition / rowHeight);
          const visibleEnd = Math.min(visibleStart + visibleRows, totalRooms);
          
          for (let i = visibleStart; i < visibleEnd; i++) {
              if (!loadedRows.has(i)) {
                  renderRow(rooms[i]);
                  loadedRows.add(i);
              }
          }
      }
      
      // Listen for scroll events
      calendarContainer.addEventListener('scroll', debounce(loadVisibleRooms, 100));

2. Optimize DOM updates by using document fragments:

   .. code-block:: javascript

      function renderBatch(rooms) {
          const fragment = document.createDocumentFragment();
          
          for (const room of rooms) {
              const row = document.createElement('tr');
              // Add cells to the row
              fragment.appendChild(row);
          }
          
          tableBody.appendChild(fragment);
      }

3. Consider using a virtualized table implementation for very large data sets

Mobile View Issues
------------------

**Issue**: Layout problems on mobile devices

**Solution**:

1. Ensure viewport meta tag is correctly set:

   .. code-block:: html

      <meta name="viewport" content="width=device-width, initial-scale=1.0">

2. Use responsive design principles:

   .. code-block:: css

      @media (max-width: 768px) {
          .booking-item {
              width: 100%;
          }
          
          .booking-table td {
              padding: 5px;
              font-size: 0.9rem;
          }
          
          /* More mobile-specific styles */
      }

3. Test on various screen sizes and devices using browser developer tools

**Issue**: Touch interactions not working correctly

**Solution**:

1. Add touch event handlers alongside mouse events:

   .. code-block:: javascript

      element.addEventListener('click', handleInteraction);
      element.addEventListener('touchend', function(e) {
          e.preventDefault(); // Prevent double events
          handleInteraction(e);
      });

2. Increase the size of touch targets:

   .. code-block:: css

      .touch-button {
          min-width: 44px;
          min-height: 44px;
          padding: 12px;
      }

3. Test on actual mobile devices rather than just emulators

Browser Compatibility Issues
----------------------------

**Issue**: Features not working in specific browsers

**Solution**:

1. Use feature detection instead of browser detection:

   .. code-block:: javascript

      if ('localStorage' in window) {
          // Browser supports localStorage
      } else {
          // Provide fallback
      }

2. Add polyfills for newer JavaScript features:

   .. code-block:: html

      <!-- Add polyfills based on what's needed -->
      <script src="https://cdn.jsdelivr.net/npm/promise-polyfill@8/dist/polyfill.min.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/fetch-polyfill@0.8.2/fetch.min.js"></script>

3. Test in multiple browsers and versions

**Issue**: CSS rendering differences between browsers

**Solution**:

1. Use a CSS reset or normalize.css:

   .. code-block:: html

      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css">

2. Add vendor prefixes for CSS properties where needed:

   .. code-block:: css

      .element {
          -webkit-box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
          -moz-box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
          box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
      }

3. Consider using a tool like Autoprefixer to automatically add vendor prefixes
