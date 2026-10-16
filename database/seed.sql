-- Dummy data for local development.
-- Run: docker compose exec -T db psql -U postgres -d ticketflow < database/seed.sql
-- All seeded users have password: password123

BEGIN;

INSERT INTO "Users" (id, name, email, password, role, create_date) VALUES
  (2, 'Ali Khan',      'ali.organizer@example.com',  '$2b$12$cs7w5RA.8mmLkbHV1RNCF.vb1ZWReZxB7vwJaWTFjQ21BcKDJSD32', 'organizer', NOW()),
  (3, 'Sara Ahmed',    'sara.organizer@example.com', '$2b$12$cs7w5RA.8mmLkbHV1RNCF.vb1ZWReZxB7vwJaWTFjQ21BcKDJSD32', 'organizer', NOW()),
  (4, 'Bilal Hussain', 'bilal@example.com',          '$2b$12$cs7w5RA.8mmLkbHV1RNCF.vb1ZWReZxB7vwJaWTFjQ21BcKDJSD32', 'customer',  NOW()),
  (5, 'Fatima Noor',   'fatima@example.com',         '$2b$12$cs7w5RA.8mmLkbHV1RNCF.vb1ZWReZxB7vwJaWTFjQ21BcKDJSD32', 'customer',  NOW()),
  (6, 'Usman Tariq',   'usman@example.com',          '$2b$12$cs7w5RA.8mmLkbHV1RNCF.vb1ZWReZxB7vwJaWTFjQ21BcKDJSD32', 'customer',  NOW());

INSERT INTO "Events" (id, org_id, title, venue, city, category, event_status, start_at_datetime) VALUES
  (1, 2, 'Lahore Music Fest',     'Alhamra Arts Council', 'Lahore',    'music',  'published', '2026-11-20 19:00'),
  (2, 2, 'Tech Summit 2026',      'Expo Centre',          'Karachi',   'tech',   'published', '2026-12-05 09:00'),
  (3, 3, 'Stand-up Comedy Night', 'The Comedy Club',      'Islamabad', 'comedy', 'published', '2026-11-08 20:00'),
  (4, 3, 'PSL Final Screening',   'Gaddafi Stadium',      'Lahore',    'sports', 'published', '2027-03-15 18:00'),
  (5, 2, 'Food Carnival',         'Beach Park',           'Karachi',   'food',   'draft',     '2027-01-10 12:00');

-- available_seats = total_seats minus tickets held by pending/confirmed bookings below
INSERT INTO "TicketType" (id, event_id, name, price, total_seats, available_seats) VALUES
  (1, 1, 'General',   2000,  500,  495),
  (2, 1, 'VIP',       5000,  100,   99),
  (3, 2, 'Standard',  3500,  300,  298),
  (4, 2, 'Premium',   8000,   50,   49),
  (5, 3, 'General',   1500,  200,  200),
  (6, 4, 'Enclosure', 1000, 1000,  996),
  (7, 4, 'VIP Box',  10000,   20,   20),
  (8, 5, 'Entry',      500,  800,  800);

INSERT INTO "Booking" (id, customer_id, event_id, booking_status, total_amount, expire_at, create_date) VALUES
  (1, 4, 1, 'confirmed', 9000, '2026-11-20 19:00', NOW()),
  (2, 5, 1, 'pending',   6000, '2026-11-20 19:00', NOW()),
  (3, 6, 2, 'confirmed', 8000, '2026-12-05 09:00', NOW()),
  (4, 4, 3, 'cancelled', 3000, '2026-11-08 20:00', NOW()),
  (5, 1, 4, 'confirmed', 4000, '2027-03-15 18:00', NOW()),
  (6, 5, 2, 'confirmed', 7000, '2026-12-05 09:00', NOW());

INSERT INTO "BookingItem" (id, booking_id, ticket_type_id, quantity, unit_price) VALUES
  (1, 1, 1, 2, 2000),
  (2, 1, 2, 1, 5000),
  (3, 2, 1, 3, 2000),
  (4, 3, 4, 1, 8000),
  (5, 4, 5, 2, 1500),
  (6, 5, 6, 4, 1000),
  (7, 6, 3, 2, 3500);

INSERT INTO "Payment" (id, booking_id, amount, status, paid_at) VALUES
  (1, 1, 9000, 'success', NOW()),
  (2, 3, 8000, 'success', NOW()),
  (3, 4, 3000, 'failed',  NOW()),
  (4, 5, 4000, 'success', NOW()),
  (5, 6, 7000, 'success', NOW());

-- Move ID sequences past the explicit IDs so the API can keep inserting
SELECT setval(pg_get_serial_sequence('"Users"', 'id'),       (SELECT MAX(id) FROM "Users"));
SELECT setval(pg_get_serial_sequence('"Events"', 'id'),      (SELECT MAX(id) FROM "Events"));
SELECT setval(pg_get_serial_sequence('"TicketType"', 'id'),  (SELECT MAX(id) FROM "TicketType"));
SELECT setval(pg_get_serial_sequence('"Booking"', 'id'),     (SELECT MAX(id) FROM "Booking"));
SELECT setval(pg_get_serial_sequence('"BookingItem"', 'id'), (SELECT MAX(id) FROM "BookingItem"));
SELECT setval(pg_get_serial_sequence('"Payment"', 'id'),     (SELECT MAX(id) FROM "Payment"));

COMMIT;
