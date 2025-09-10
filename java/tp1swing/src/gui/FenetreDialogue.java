package gui ;
import javax.swing.*;
public class FenetreDialogue extends JDialog {
    private JPanel myContentPane;
    private JLabel lNom;
    private JTextField tfNom;
    private JButton bOK ;
    private JButton bAnnuler ;
    public FenetreDialogue() {
        setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE);
        setBounds(200, 200, 400, 200);
        setTitle("Ma fenetre de dialogue");
        myContentPane = new JPanel();
        myContentPane.setLayout(null);
        setContentPane(myContentPane);
        lNom = new JLabel("Nom : ");
        lNom.setBounds(50,50,100,20);
        myContentPane.add(lNom);
        tfNom = new JTextField();
        tfNom.setBounds(200,50,150,20);
        myContentPane.add(tfNom);
        bOK = new JButton("OK");
        bOK.setBounds(50,100,100,20);
        myContentPane.add(bOK);
        bAnnuler = new JButton("OK");
        bAnnuler.setBounds(50,100,100,20);
        myContentPane.add(bAnnuler);
    }
}