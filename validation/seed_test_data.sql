-- Seed data for manually testing Component 2 (Validation Engine) against the
-- real central_bank_system DB. Uses high IDs (9001+) to avoid clashing with
-- real records, and ON DUPLICATE KEY UPDATE so it's safe to re-run.
--
-- Run with: mysql -u root central_bank_system < seed_test_data.sql

USE central_bank_system;

-- Task 2.1 fixture: bank starts ineligible
INSERT INTO commercial_banks (bank_id, bank_name, password_hash, eligibility, borrowing_limit)
VALUES (9001, 'Test_Bank_A', 'x', 'none', 1000000)
ON DUPLICATE KEY UPDATE eligibility = 'none', borrowing_limit = 1000000;

-- Task 2.2 / 2.3 fixtures: an admissible collateral type + a pledged asset
-- haircut_percentage is percentage points (10.00 = 10%), matching DECIMAL(5,2)
INSERT INTO collateral_types (collateral_type_id, type_name, haircut_percentage)
VALUES (9001, 'Government Bond', 10.00)
ON DUPLICATE KEY UPDATE type_name = 'Government Bond', haircut_percentage = 10.00;

INSERT INTO collateral_inventory (inventory_id, bank_id, collateral_type_id, declared_value)
VALUES (9001, 9001, 9001, 300000)
ON DUPLICATE KEY UPDATE declared_value = 300000;

INSERT INTO weekly_operations (operation_id, start_date, end_date, status)
VALUES (9001, CURDATE(), CURDATE() + INTERVAL 7 DAY, 'Open')
ON DUPLICATE KEY UPDATE status = 'Open';

-- Matches the doc's test: 500,000 requested against a 300,000 asset w/ 10% haircut -> FAIL
INSERT INTO requests (request_id, bank_id, operation_id, requested_amount, status)
VALUES (9001, 9001, 9001, 500000, 'Pending')
ON DUPLICATE KEY UPDATE requested_amount = 500000, status = 'Pending';

INSERT IGNORE INTO request_collateral (request_id, inventory_id)
VALUES (9001, 9001);

-- ── To flip each check to PASS, run these afterwards ──────────────────
-- UPDATE commercial_banks SET eligibility = 'eligible' WHERE bank_id = 9001;   -- 2.1 -> PASS
-- UPDATE requests SET requested_amount = 250000 WHERE request_id = 9001;       -- 2.3 -> PASS
