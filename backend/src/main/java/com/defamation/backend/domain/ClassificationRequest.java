package com.defamation.backend.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "classification_requests")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ClassificationRequest {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // input
    @Lob
    @Column(name = "problem_situation", columnDefinition = "LONGTEXT", nullable = false)
    private String problemSituation;

    // ✅ 어떤 모델로 분류했는지 (FK models.id)
    @Column(name = "model_id", nullable = false)
    private Long modelId;

    // output
    @Lob
    @Column(name = "case_names", columnDefinition = "json")
    private String caseNames; // JSON 문자열로 저장

    @Column(name = "sentence_type", length = 50)
    private String sentenceType;

    @Column(name = "sentence_value")
    private Long sentenceValue;

    @Column(name = "sentence_suspension")
    private Integer sentenceSuspension;

    @Lob
    @Column(name = "sentence_additional_order", columnDefinition = "LONGTEXT")
    private String sentenceAdditionalOrder;

    @Lob
    @Column(name = "sentence_reason", columnDefinition = "LONGTEXT")
    private String sentenceReason;

    @Column(name = "sentence_judgment", length = 20)
    private String sentenceJudgment;

    @Builder.Default
    @Column(name = "is_deleted", nullable = false)
    private Boolean isDeleted = false;

    // DB default CURRENT_TIMESTAMP 사용
    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;
}
