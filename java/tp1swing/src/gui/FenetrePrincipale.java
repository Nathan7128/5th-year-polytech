package gui;

import javax.swing.* ;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class FenetrePrincipale extends JFrame {
    private JPanel myContentPane ;
    private JLabel lNom, lPrenom, lAge, lAdresse;
    private JTextField tfNom, tfPrenom, tfAge;
    private JTextArea tfAdresse;
    private JMenuBar menuBar;
    private JMenu mFichier;
    private JMenuItem miQuitter, miActions, miRemplir, miVider, miChangerNom, miRemplir2, miVider2;
    JToolBar toolBar;
    FenetreDialogue fdChangerNom;

    public FenetrePrincipale()
    {
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setBounds(100, 100, 800, 600);
        setTitle("Ma premiere fenetre en Java");
        myContentPane = new JPanel() ;
        myContentPane.setLayout(null) ;
        setContentPane(myContentPane) ;

        lNom = new JLabel("Nom : ");
        lNom.setBounds(50,100,100,20);
        myContentPane.add(lNom);
        tfNom = new JTextField();
        tfNom.setBounds(200,100,550,20);
        myContentPane.add(tfNom);

        lPrenom = new JLabel("Prénom : ");
        lPrenom.setBounds(50,150,100,20);
        myContentPane.add(lPrenom);
        tfPrenom = new JTextField();
        tfPrenom.setBounds(200,150,550,20);
        myContentPane.add(tfPrenom);

        lAge = new JLabel("Age : ");
        lAge.setBounds(50,200,100,20);
        myContentPane.add(lAge);
        tfAge = new JTextField();
        tfAge.setBounds(200,200,550,20);
        myContentPane.add(tfAge);

        lAdresse = new JLabel("Adresse : ");
        lAdresse.setBounds(50,250,100,20);
        myContentPane.add(lAdresse);
        tfAdresse = new JTextArea();
        tfAdresse.setBounds(200,250,550,100);
        myContentPane.add(tfAdresse);

        menuBar = new JMenuBar();
        menuBar.setBounds(0, 0, 440, 21);
        myContentPane.add(menuBar);

        mFichier = new JMenu("Fichier");
        menuBar.add(mFichier);
        miQuitter = new JMenuItem("Quitter");
        mFichier.add(miQuitter) ;

        miQuitter.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                dispose();
            }
        });

        miActions = new JMenu("Actions");
        menuBar.add(miActions);

        miRemplir = new JMenuItem("Remplir");
        miActions.add(miRemplir);
        miRemplir.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                remplir(e);
            }
        });

        miVider = new JMenuItem("Vider");
        miActions.add(miVider);
        miVider.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                vider(e);
            }
        });

        fdChangerNom = new FenetreDialogue();
        miChangerNom = new JMenuItem("Modifier nom");
        miActions.add(miChangerNom);
        miChangerNom.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                fdChangerNom.setVisible(true);
            }
        });

        toolBar = new JToolBar();
        toolBar.setBounds(0, 21, 800, 30);
        myContentPane.add(toolBar);

        miRemplir2 = new JMenuItem("Remplir");
        toolBar.add(miRemplir2);
        miRemplir2.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                remplir(e);
            }
        });

        miVider2 = new JMenuItem("Vider");
        toolBar.add(miVider2);
        miVider2.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                vider(e);
            }
        });
    }

    public void remplir(ActionEvent e)
    {
        tfNom.setText("Guillet");
        tfPrenom.setText("Simon");
        tfAge.setText("21");
        tfAdresse.setText("Clermont City");
    }
    public void vider(ActionEvent e)
    {
        tfNom.setText("");
        tfPrenom.setText("");
        tfAge.setText("");
        tfAdresse.setText("");
    }
}