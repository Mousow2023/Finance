CREATE TABLE purchase (
    purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer TEXT NOT NULL,
    stock TEXT NOT NULL,
    shares INTEGER NOT NULL,
    price_per_share REAL,
    total_price REAL,
    purchase_date DATETIME NOT NULL,
    UNIQUE (purchase_id),
    FOREIGN KEY (buyer) REFERENCES users(username)
);



CREATE TABLE history (
    operation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    operation_type TEXT NOT NULL,
    stock TEXT NOT NULL,
    shares INTEGER NOT NULL,
    price_per_share REAL,
    total_price REAL,
    purchase_date DATETIME NOT NULL,
    UNIQUE (operation_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

ALTER TABLE history
ADD FOREIGN KEY (user_id) REFERENCES users(id);


CREATE TABLE purchase (
    purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id INTEGER NOT NULL,
    stock TEXT NOT NULL,
    shares INTEGER NOT NULL,
    price_per_share REAL,
    total_price REAL,
    purchase_date DATETIME NOT NULL,
    UNIQUE (purchase_id),
    FOREIGN KEY (buyer_id) REFERENCES users(id)
);


DELETE FROM purchase WHERE stock = (
    SELECT DISTINCT stock FROM purchase WHERE stock = ?
)

