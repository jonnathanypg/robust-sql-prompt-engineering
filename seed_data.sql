-- Create table if it doesn't exist (Read-only agent assumes it exists, but for testing we need it)
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    status TEXT NOT NULL,
    category TEXT NOT NULL
);

-- Clear existing data to avoid duplicates during testing
TRUNCATE TABLE inventory;

-- Insert simulated data
INSERT INTO inventory (make, model, year, price, status, category) VALUES
('Toyota', 'Corolla', 2022, 22000.00, 'Available', 'Sedan'),
('Toyota', 'Camry', 2023, 28000.00, 'Available', 'Sedan'),
('Toyota', 'Rav4', 2021, 26000.00, 'Sold', 'SUV'),
('Toyota', 'Hilux', 2024, 45000.00, 'Available', 'Truck'),
('Ford', 'F-150', 2020, 35000.00, 'Available', 'Truck'),
('Ford', 'Mustang', 2023, 55000.00, 'Reserved', 'Coupe'),
('Ford', 'Explorer', 2022, 40000.00, 'Available', 'SUV'),
('Honda', 'Civic', 2019, 18000.00, 'Available', 'Sedan'),
('Honda', 'CR-V', 2023, 32000.00, 'Available', 'SUV'),
('Chevrolet', 'Silverado', 2021, 38000.00, 'Available', 'Truck'),
('Chevrolet', 'Camaro', 2018, 25000.00, 'Sold', 'Coupe'),
('Nissan', 'Sentra', 2020, 15000.00, 'Available', 'Sedan'),
('Nissan', 'Frontier', 2022, 30000.00, 'Reserved', 'Truck'),
('Volkswagen', 'Golf', 2021, 21000.00, 'Available', 'Hatchback'),
('Volkswagen', 'Tiguan', 2023, 33000.00, 'Available', 'SUV');
