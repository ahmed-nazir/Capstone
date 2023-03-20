CREATE TABLE Users (
	Username VARCHAR(32) NOT NULL PRIMARY KEY,
    FirstName VARCHAR(32),
    LastName VARCHAR(32),
    TeamRole VARCHAR(32) CHECK (TeamRole IN ('Admin', 'Team Lead', 'Member')),
    ProfileImageURL VARCHAR(500)
);

CREATE TABLE Test (
	ID INT AUTO_INCREMENT PRIMARY KEY,
    UserName VARCHAR(32) NOT NULL,
    TestName VARCHAR(100) NOT NULL,
    TestPurpose VARCHAR(500) NOT NULL,
    TestDescription VARCHAR(500) NOT NULL,
	ImageURL VARCHAR(500),
    FOREIGN KEY (UserName) REFERENCES Users(UserName)
);

CREATE TABLE Login ( 
	UserName VARCHAR(32) NOT NULL UNIQUE PRIMARY KEY,
    Salt CHAR(64) NOT NULL,
    HashPass CHAR(64) NOT NULL,
    FOREIGN KEY (UserName) REFERENCES Users(UserName)
);