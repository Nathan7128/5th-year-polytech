package gui ;
import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class FenetreDialogue extends JDialog {
    private JPanel myContentPane;
    private JLabel lNom;
    private JTextField tfNom;
    private JButton bOK ;
    private JButton bAnnuler ;
    private FenetrePrincipale fp;
    public FenetreDialogue(FenetrePrincipale fenetrePrincipale) {
        fp = fenetrePrincipale;
        setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE);
        setBounds(200, 200, 400, 200);
        setTitle("Ma fenetre de dialogue");
        myContentPane = new JPanel();
        myContentPane.setLayout(null);
        setContentPane(myContentPane);
        lNom = new JLabel("Nom : ");
        lNom.setBounds(50,50,100,20);
        myContentPane.add(lNom);
        tfNom = new JTextField(fenetrePrincipale.getNom());
        tfNom.setBounds(200,50,150,20);
        myContentPane.add(tfNom);
        bOK = new JButton("OK");
        bOK.setBounds(50,100,100,20);
        myContentPane.add(bOK);
        bOK.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                validerOk(e);
            }
        });
        bAnnuler = new JButton("Annuler");
        bAnnuler.setBounds(250,100,100,20);
        bAnnuler.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                validerAnnuler(e);
            }
        });
        myContentPane.add(bAnnuler);
    }
    public void validerOk(ActionEvent e) {
        fp.setNom(tfNom.getText());
        this.dispose();
    }
    public void validerAnnuler(ActionEvent e) {
        this.dispose();
    }
}