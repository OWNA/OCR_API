package io.owna.ocr

object App {

  def main(args: Array[String]) : Unit = {
    import cc.factorie._            // The base library: variables, factors
    import cc.factorie.la           // Linear algebra: tensors, dot-products, etc.
    import cc.factorie.optimize._   // Gradient-based optimization and training
                                    // Declare random variable types
                                    // A domain and variable type for storing words
    import cc.factorie.variable._
    import cc.factorie.model._
    import cc.factorie.infer._

    import scala.io.Source
    import scala.collection.mutable.ArrayBuffer

    class GroundTruthSegment(
      val document:Int,
      val header:Int,
      val start:Int,
      val end:Int) {}

    val groundTruthSegments = Array(
      new GroundTruthSegment(1,  12, 13, 20),
      new GroundTruthSegment(2,  11, 12, 18),
      new GroundTruthSegment(3,   9, 10, 24),
      new GroundTruthSegment(4,   8, 9,  17),
      new GroundTruthSegment(5,   8, 9,  31),
      new GroundTruthSegment(6,   8, 9,  13),
      new GroundTruthSegment(7,  15, 16, 21),
      new GroundTruthSegment(8,  10, 11, 23),
      new GroundTruthSegment(9,  12, 13, 35),
      new GroundTruthSegment(10,  9, 10, 17),
      new GroundTruthSegment(11, 15, 17, 26),
      new GroundTruthSegment(12, 11, 12, 12),
      new GroundTruthSegment(13, 13, 14, 19),
      new GroundTruthSegment(14,  7,  8, 12),
      new GroundTruthSegment(15, 13, 15, 39),
      new GroundTruthSegment(16,  7,  8, 15),
      new GroundTruthSegment(17, 14, 15, 29),
      new GroundTruthSegment(18, 12, 13, 37),
      new GroundTruthSegment(19, 18, 19, 26),
      new GroundTruthSegment(20,  8,  9, 21)
    )

    object LineFeaturesDomain extends CategoricalVectorDomain[String]

    class LineFeatures(val line:String)
        extends BinaryFeatureVectorVariable[String] {
      def domain = LineFeaturesDomain
    }

    object LabelDomain extends CategoricalDomain[String]
    class Label(str:String, val features:LineFeatures)
        extends LabeledCategoricalVariable(str){
      def domain = LabelDomain
    }
    class LabelSeq extends scala.collection.mutable.ArrayBuffer[Label]

    val labelSequences = groundTruthSegments.map(s => {
      var index = 0
      val filename = s"../../data/processed/B/${s.document}A-p1.txt"
      new LabelSeq ++= Source.fromFile(filename).getLines()
        .filterNot(_.trim.isEmpty).map(rawLine => {
          val line = rawLine.trim()
          index += 1
          var label = "NON_TABLE"
          if (index == s.header) {
            label = "HEADER"
          }
          if (index >= s.start && index <= s.end) {
            label = "TABLE_LINE"
          }
          val features = new LineFeatures(line)
          if (line.matches(".*\\d.*")) {
            features += "HAS_NUMERIC=1"
          }
          if (line.matches(".*\\d.*\\s.*\\d.*")) {
            features += "HAS_NUMERIC=2"
          }
          if (line.matches(".*\\d.*\\s.*\\d.*\\s.*\\d.*")) {
            features += "HAS_NUMERIC=3"
          }
          new Label(label, features)
        })
    })

    val model = new Model with Parameters {
      val markov = new DotFamilyWithStatistics2[Label,Label] {
        val weights = Weights(new la.DenseTensor2(
          LabelDomain.size, LabelDomain.size))
      }
      val observ = new DotFamilyWithStatistics2[Label,LineFeatures] {
        val weights = Weights(new la.DenseTensor2(
          LabelDomain.size, LineFeaturesDomain.dimensionSize))
      }
      def factors(labels:Iterable[Var]) = labels match {
        case labels:LabelSeq =>
          labels.map(label =>
            new observ.Factor(label, label.features)) ++
            labels.sliding(2).map(window => new markov.Factor(
              window.head, window.last))
      }
    }

    val optimizer0 = new optimize.AdaGrad()
    val trainer = new SynchronizedOptimizerOnlineTrainer(model.parameters, optimizer0)
    val (trainSequences, testSequences) = labelSequences.splitAt(15)
    trainer.trainFromExamples(trainSequences.map(
      labels => new LikelihoodExample(labels, model, InferByBPChain)))
    testSequences.foreach(labelSequence => {
      val summary = BP.inferChainSum(labelSequence, model)
      for (label <- labelSequence) {
        val result = LabelDomain.categories.zip(
          summary.marginal(label).proportions.asSeq)
          .sortBy(_._2).reverse.mkString(" ")
        println(label.value + " " + result)
      }
    })
  }
}
