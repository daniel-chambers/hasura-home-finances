CREATE TABLE IF NOT EXISTS public."Transaction"
(
    "Id" integer NOT NULL,
    "TransactionDate" date NOT NULL,
    "Amount" numeric NOT NULL,
    "Description" text COLLATE pg_catalog."default" NOT NULL,
    "ReceiptNum" text COLLATE pg_catalog."default",
    CONSTRAINT "Transaction_pkey" PRIMARY KEY ("Id")
);

CREATE TABLE IF NOT EXISTS public."Category"
(
    "Name" text COLLATE pg_catalog."default" NOT NULL,
    "Deprecated" bit(1) NOT NULL,
    "ParentCategory" text COLLATE pg_catalog."default",
    CONSTRAINT "Category_pkey" PRIMARY KEY ("Name"),
    CONSTRAINT "FK_Category_ParentCategory" FOREIGN KEY ("ParentCategory")
        REFERENCES public."Category" ("Name") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS public."TransactionCategory"
(
    "TransactionId" integer NOT NULL,
    "CategoryName" text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "TransactionCategory_pkey" PRIMARY KEY ("TransactionId", "CategoryName"),
    CONSTRAINT "FK_TransactionCategory_CategoryName" FOREIGN KEY ("CategoryName")
        REFERENCES public."Category" ("Name") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "FK_TransactionCategory_TransactionId" FOREIGN KEY ("TransactionId")
        REFERENCES public."Transaction" ("Id") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);
