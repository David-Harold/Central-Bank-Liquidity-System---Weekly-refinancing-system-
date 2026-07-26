DROP DATABASE IF EXISTS central_bank_system;
CREATE DATABASE central_bank_system;

USE central_bank_system;

CREATE TABLE central_bank (
	central_bank_id VARCHAR(50) PRIMARY KEY NOT NULL UNIQUE,
	password_hash VARCHAR(250) NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE commercial_banks (
	bank_id INT PRIMARY KEY AUTO_INCREMENT,
	bank_name VARCHAR(250) NOT NULL,
	password_hash VARCHAR(250) NOT NULL,
	eligibility ENUM('none','eligible') NOT NULL,
	borrowing_limit DECIMAL(15,2) NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE collateral_types (
	collateral_type_id INT PRIMARY KEY AUTO_INCREMENT,
	type_name VARCHAR(250) NOT NULL,
	haircut_percentage DECIMAL(5,2) NOT NULL
);

CREATE TABLE collateral_inventory (
	inventory_id INT PRIMARY KEY AUTO_INCREMENT,
	bank_id INT NOT NULL,
	collateral_type_id INT NOT NULL,
	declared_value DECIMAL(15,2) NOT NULL,
	FOREIGN KEY(bank_id) REFERENCES commercial_banks(bank_id),
	FOREIGN KEY(collateral_type_id) REFERENCES collateral_types(collateral_type_id)
);

CREATE TABLE weekly_operations (
	operation_id INT PRIMARY KEY AUTO_INCREMENT,
	start_date DATE NOT NULL,
	end_date DATE NOT NULL,
	status ENUM('Open','Closed') NOT NULL
);

CREATE TABLE requests (
	request_id INT PRIMARY KEY AUTO_INCREMENT,
	bank_id INT NOT NULL,
	operation_id INT NOT NULL,
	requested_amount DECIMAL(15,2) NOT NULL,
	status ENUM('Pending','Successful','Failed') NOT NULL,
	FOREIGN KEY(bank_id) REFERENCES commercial_banks(bank_id),
	FOREIGN KEY(operation_id) REFERENCES weekly_operations(operation_id)
);

CREATE TABLE request_collateral (
	request_id INT NOT NULL,
	inventory_id INT NOT NULL,
    PRIMARY KEY(request_id, inventory_id),
	FOREIGN KEY(inventory_id) REFERENCES collateral_inventory(inventory_id),
	FOREIGN KEY(request_id) REFERENCES requests(request_id)
);

CREATE TABLE rejections (
	rejection_id INT PRIMARY KEY AUTO_INCREMENT,
	request_id INT NOT NULL,
	rejection_reason TEXT NOT NULL,
	rejection_date DATETIME,
	FOREIGN KEY(request_id) REFERENCES requests(request_id)
);

CREATE TABLE allotments (
	allotment_id INT PRIMARY KEY AUTO_INCREMENT,
	request_id INT NOT NULL,
	approved_amount DECIMAL(15,2) NOT NULL,
	policy_rate DECIMAL(5,2) NOT NULL,
	FOREIGN KEY(request_id) REFERENCES requests(request_id)
);

CREATE TABLE settlements (
	settlement_id INT PRIMARY KEY AUTO_INCREMENT,
	allotment_id INT NOT NULL,
	settlement_date DATETIME NOT NULL,
	repayment_date DATETIME NOT NULL,
	interest_amount DECIMAL(15,2) NOT NULL,
	FOREIGN KEY(allotment_id) REFERENCES allotments(allotment_id)
);
