import sg.edu.nus.iss.se24_2ft.unit1.ca.category.*;
import sg.edu.nus.iss.se24_2ft.unit1.ca.customer.member.*;
import sg.edu.nus.iss.se24_2ft.unit1.ca.discount.*;
import sg.edu.nus.iss.se24_2ft.unit1.ca.product.*;
import sg.edu.nus.iss.se24_2ft.unit1.ca.transaction.*;
import java.nio.file.*; import java.util.*;

public class Probe {
    static Path D;
    static void reset() throws Exception {
        D = Files.createTempDirectory("pos");
        for (Path p : Files.newDirectoryStream(Paths.get(System.getProperty("sample"))))
            Files.copy(p, D.resolve(p.getFileName()));
    }
    static String f(String n) { return D.resolve(n).toString(); }
    public static void main(String[] a) throws Exception {
        // P1: member transactions lose their member on reload/rewrite
        reset();
        CategoryManager cm = new CategoryManager(f("Category.dat"));
        ProductManager pm = new ProductManager(f("Products.dat"), cm);
        pm.getTableModel(); pm.getUnderstockTableModel();
        MemberManager mm = new MemberManager(f("Members.dat"));
        TransactionManager tm = new TransactionManager(f("Transactions.dat"), pm, mm);
        System.out.println("P1 before: " + Files.readAllLines(D.resolve("Transactions.dat")));
        Transaction t = new Transaction();
        t.addTransactionItem(new TransactionItem(pm.getProduct("SNA/2"), 1));
        t.setPayment(10); t.setDate(new Date());
        tm.addTransaction(t);
        System.out.println("P1 after : " + Files.readAllLines(D.resolve("Transactions.dat")));

        // P2: deductQuantity NPE when understock table model not yet created
        reset();
        cm = new CategoryManager(f("Category.dat"));
        pm = new ProductManager(f("Products.dat"), cm);
        try { pm.deductQuantity("CLO/2", 395); System.out.println("P2 no error"); }
        catch (Exception e) { System.out.println("P2 " + e); }

        // P3: lowercase category id accepted but never retrievable
        reset();
        cm = new CategoryManager(f("Category.dat"));
        cm.addCategory(new Category("bks", "Books"));
        System.out.println("P3 getCategory(\"bks\") = " + cm.getCategory("bks"));

        // P4: comma in product name corrupts the CSV file
        reset();
        cm = new CategoryManager(f("Category.dat"));
        pm = new ProductManager(f("Products.dat"), cm);
        pm.addProduct(cm.getCategory("MUG"), new Product("Mug, Large", "Big", 10, 5.0, 777, 2, 5));
        List<String> lines = Files.readAllLines(D.resolve("Products.dat"));
        System.out.println("P4 stored: " + lines.stream().filter(l -> l.startsWith("MUG/3")).findFirst().get());
        ProductManager pm2 = new ProductManager(f("Products.dat"), new CategoryManager(f("Category.dat")));
        Product reloaded = pm2.getProduct("MUG/3");
        System.out.println("P4 reloaded name='" + reloaded.getName() + "' desc='" + reloaded.getDescription()
            + "' qty=" + reloaded.getQuantity() + " price=" + reloaded.getPrice());

        // P5: one malformed line aborts the entire load (constructor throws)
        reset();
        Files.write(D.resolve("Members.dat"), Arrays.asList("Good Person,M001,10", "BrokenLineNoCommas", "Other,M002,5"));
        try { new MemberManager(f("Members.dat")); System.out.println("P5 loaded ok"); }
        catch (Exception e) { System.out.println("P5 " + e); }

        // P6: duplicate discount silently rejected (boolean ignored by GUI wiring)
        reset();
        DiscountManager dm = new DiscountManager(f("Discounts.dat"));
        System.out.println("P6 addDiscount duplicate returns " +
            dm.addDiscount(new Discount("CENTENARY", "dup", null, -1, 99, false)));

        // P7: active discount today for public and members (2014 promotions all expired)
        System.out.println("P7 public max discount = " + dm.getMaxDiscount(sg.edu.nus.iss.se24_2ft.unit1.ca.customer.PublicCustomer.getInstance()));
        mm = new MemberManager(f("Members.dat"));
        System.out.println("P7 new member (pts -1) = " + dm.getMaxDiscount(mm.getMember("R64565FG4")).getCode()
            + ", existing member = " + dm.getMaxDiscount(mm.getMember("F42563743156")).getCode());

        // P8: Transaction.getId() before checkout throws NPE (Integer unboxing)
        try { new Transaction().getId(); } catch (Exception e) { System.out.println("P8 " + e); }
    }
}
