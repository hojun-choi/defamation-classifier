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
    @Column(name="problem_situation", nullable=false, columnDefinition="LONGTEXT")
    private String problemSituation;

    // model outputs (RAW -> 매핑 결과)
    @Column(name="case_names", columnDefinition="JSON")
    private String caseNames;   // JSON string (죄명 리스트)

    @Column(name="sentence_type")
    private String sentenceType; // 형종

    @Column(name="sentence_value")
    private Long sentenceValue;  // 벌금액(숫자)

    @Column(name="sentence_suspension")
    private Integer sentenceSuspension; // 집유 기간 월

    @Lob
    @Column(name="sentence_additional_order", columnDefinition="LONGTEXT")
    private String sentenceAdditionalOrder; // 추가 조건

    @Lob
    @Column(name="sentence_reason", columnDefinition="LONGTEXT")
    private String sentenceReason;          // 양형 이유

    @Column(name="sentence_judgment")
    private String sentenceJudgment;        // 판단

    @Builder.Default
    @Column(name="is_deleted", nullable=false)
    private Boolean isDeleted = false;

    @Column(name="created_at", insertable=false, updatable=false)
    private LocalDateTime createdAt;
}
